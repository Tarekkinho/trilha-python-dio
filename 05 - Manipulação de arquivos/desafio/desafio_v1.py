from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List


class Historico:
    def __init__(self):
        self.transacoes = []

    def registrar(self, tipo, valor):
        self.transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
        })

    def listar(self):
        for t in self.transacoes:
            yield t

    def do_dia(self):
        hoje = datetime.utcnow().date()
        return [t for t in self.transacoes if datetime.strptime(t["data"], "%d-%m-%Y %H:%M:%S").date() == hoje]


@dataclass
class Cliente:
    nome: str
    cpf: str
    nascimento: str
    endereco: str
    contas: List["Conta"] = field(default_factory=list)

    def adicionar_conta(self, conta: "Conta"):
        self.contas.append(conta)

    def realizar_transacao(self, conta, transacao: "Transacao"):
        if len(conta.historico.do_dia()) >= 2:
            print("\n@@@ Limite diário de transações atingido! @@@")
            return
        transacao.executar(conta)


@dataclass
class Conta:
    cliente: Cliente
    numero: int
    agencia: str = "0001"
    saldo: float = 0.0
    historico: Historico = field(default_factory=Historico)

    def sacar(self, valor):
        if valor <= 0:
            print("Valor inválido para saque.")
            return False
        if valor > self.saldo:
            print("Saldo insuficiente.")
            return False
        self.saldo -= valor
        self.historico.registrar("Saque", valor)
        print("Saque realizado com sucesso.")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido para depósito.")
            return False
        self.saldo += valor
        self.historico.registrar("Depósito", valor)
        print("Depósito realizado com sucesso.")
        return True


@dataclass
class ContaCorrente(Conta):
    limite: float = 500.0
    limite_saques: int = 3

    def sacar(self, valor):
        saques = [t for t in self.historico.transacoes if t["tipo"] == "Saque"]
        if len(saques) >= self.limite_saques:
            print("Limite de saques excedido.")
            return False
        if valor > self.limite:
            print("Valor excede o limite permitido.")
            return False
        return super().sacar(valor)


class Transacao(ABC):
    def __init__(self, valor):
        self.valor = valor

    @abstractmethod
    def executar(self, conta: Conta):
        ...


class Saque(Transacao):
    def executar(self, conta: Conta):
        conta.sacar(self.valor)


class Deposito(Transacao):
    def executar(self, conta: Conta):
        conta.depositar(self.valor)


# ========== Interface Simples ==========

def menu():
    print("""
[d] Depositar
[s] Sacar
[e] Extrato
[nc] Nova Conta
[nu] Novo Cliente
[lc] Listar Contas
[q] Sair
""")
    return input("Escolha a opção: ").strip()


def buscar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def criar_cliente(clientes):
    cpf = input("CPF: ")
    if buscar_cliente(cpf, clientes):
        print("Cliente já existe.")
        return
    nome = input("Nome: ")
    nascimento = input("Nascimento: ")
    endereco = input("Endereço: ")
    clientes.append(Cliente(nome, cpf, nascimento, endereco))
    print("Cliente criado com sucesso.")


def criar_conta(clientes, contas):
    cpf = input("CPF do cliente: ")
    cliente = buscar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return
    numero = len(contas) + 1
    conta = ContaCorrente(cliente=cliente, numero=numero)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    print("Conta criada com sucesso.")


def realizar_transacao(clientes, tipo):
    cpf = input("CPF do cliente: ")
    cliente = buscar_cliente(cpf, clientes)
    if not cliente or not cliente.contas:
        print("Cliente ou conta inválida.")
        return
    valor = float(input("Valor: "))
    conta = cliente.contas[0]  # simplificação
    transacao = Saque(valor) if tipo == "saque" else Deposito(valor)
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = buscar_cliente(cpf, clientes)
    if not cliente or not cliente.contas:
        print("Cliente ou conta inválida.")
        return
    conta = cliente.contas[0]
    print(f"Saldo atual: R$ {conta.saldo:.2f}")
    print("Transações:")
    for t in conta.historico.listar():
        print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")


def listar_contas(contas):
    for conta in contas:
        print(f"Agência: {conta.agencia}, Número: {conta.numero}, Cliente: {conta.cliente.nome}, Saldo: R$ {conta.saldo:.2f}")


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()
        if opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(clientes, contas)
        elif opcao == "d":
            realizar_transacao(clientes, "deposito")
        elif opcao == "s":
            realizar_transacao(clientes, "saque")
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
