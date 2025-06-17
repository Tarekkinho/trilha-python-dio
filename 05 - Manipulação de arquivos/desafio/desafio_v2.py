from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import textwrap

ROOT_PATH = Path(__file__).parent


# === CLASSES AUXILIARES ===

class ContasIterador:
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._contas):
            raise StopIteration

        conta = self._contas[self._index]
        self._index += 1
        return textwrap.dedent(f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """)


# === CLIENTES ===

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("\n@@@ Limite diário de transações atingido! @@@")
            return

        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = nascimento
        self.cpf = cpf

    def __repr__(self):
        return f"<PessoaFisica: {self.nome} | CPF: {self.cpf}>"


# === CONTAS ===

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
        })

    def gerar_relatorio(self, tipo=None):
        for t in self._transacoes:
            if tipo is None or t["tipo"].lower() == tipo.lower():
                yield t

    def transacoes_do_dia(self):
        hoje = datetime.utcnow().date()
        return [
            t for t in self._transacoes
            if datetime.strptime(t["data"], "%d-%m-%Y %H:%M:%S").date() == hoje
        ]


class Conta:
    def __init__(self, numero, cliente):
        self._numero = numero
        self._cliente = cliente
        self._saldo = 0
        self._agencia = "0001"
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para saque. @@@")
            return False
        if valor > self.saldo:
            print("\n@@@ Saldo insuficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para depósito. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques = sum(1 for t in self.historico.transacoes if t["tipo"] == "Saque")

        if valor > self._limite:
            print("\n@@@ Saque excede o limite permitido. @@@")
            return False
        if saques >= self._limite_saques:
            print("\n@@@ Limite de saques atingido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return textwrap.dedent(f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """)

    def __repr__(self):
        return f"<ContaCorrente: {self.agencia} - {self.numero} - {self.cliente.nome}>"


# === TRANSACOES ===

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


# === FUNÇÕES AUXILIARES ===

def log_transacao(func):
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        with open(ROOT_PATH / "log.txt", "a") as f:
            f.write(f"[{datetime.utcnow()}] Função {func.__name__}({args}, {kwargs}) => {resultado}\n")
        return resultado
    return wrapper


def menu():
    return input(textwrap.dedent("""
        \n======= MENU =======
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [nc] Nova conta
        [lc] Listar contas
        [nu] Novo usuário
        [q] Sair
        => """))


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente sem conta. @@@")
        return None
    return cliente.contas[0]


# === OPERAÇÕES ===

@log_transacao
def depositar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    valor = float(input("Valor do depósito: "))
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, Deposito(valor))


@log_transacao
def sacar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    valor = float(input("Valor do saque: "))
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, Saque(valor))


@log_transacao
def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    conta = recuperar_conta_cliente(cliente)

    if conta:
        print("\n====== EXTRATO ======")
        for t in conta.historico.gerar_relatorio():
            print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
        print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
        print("=======================")


@log_transacao
def criar_cliente(clientes):
    cpf = input("CPF: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Cliente já cadastrado. @@@")
        return

    nome = input("Nome completo: ")
    nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço: ")

    clientes.append(PessoaFisica(nome, nascimento, cpf, endereco))
    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero, clientes, contas):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = ContaCorrente.nova_conta(cliente, numero, limite=500, limite_saques=50)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta_str in ContasIterador(contas):
        print("=" * 50)
        print(conta_str)


# === MAIN ===

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu().lower()

        match opcao:
            case "d": depositar(clientes)
            case "s": sacar(clientes)
            case "e": exibir_extrato(clientes)
            case "nu": criar_cliente(clientes)
            case "nc":
                numero = len(contas) + 1
                criar_conta(numero, clientes, contas)
            case "lc": listar_contas(contas)
            case "q":
                print("Saindo...")
                break
            case _: print("\n@@@ Opção inválida. Tente novamente. @@@")

if __name__ == "__main__":
    main()
