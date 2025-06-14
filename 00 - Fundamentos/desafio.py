"""
Sistema Bancário Simples em Python

Este script implementa um sistema bancário com as operações básicas:
depósito, saque, extrato e encerramento. Regras de limite de saque e
número máximo de saques por dia são aplicadas.

Autor: Tarek
Data: 2025-06-14
"""

LIMITE_SAQUE = 500
MAX_SAQUES_DIARIOS = 3

def exibir_menu():
    menu = """
=============== MENU ===============

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """
    return input(menu).lower()


def depositar(saldo, extrato):
    valor = float(input("Informe o valor do depósito: "))

    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print(f"✅ Depósito de R$ {valor:.2f} realizado com sucesso.")
    else:
        print("❌ Operação falhou! Valor inválido para depósito.")

    return saldo, extrato


def sacar(saldo, extrato, numero_saques):
    valor = float(input("Informe o valor do saque: "))

    if valor <= 0:
        print("❌ Operação falhou! Valor inválido para saque.")

    elif valor > saldo:
        print("❌ Operação falhou! Saldo insuficiente.")

    elif valor > LIMITE_SAQUE:
        print(f"❌ Operação falhou! Limite por saque é R$ {LIMITE_SAQUE:.2f}.")

    elif numero_saques >= MAX_SAQUES_DIARIOS:
        print("❌ Operação falhou! Número máximo de saques diários atingido.")

    else:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        print(f"✅ Saque de R$ {valor:.2f} realizado com sucesso.")

    return saldo, extrato, numero_saques


def exibir_extrato(saldo, extrato):
    print("\n=============== EXTRATO ===============")
    print("Não foram realizadas movimentações." if not extrato else extrato.strip())
    print(f"\nSaldo atual: R$ {saldo:.2f}")
    print("=======================================\n")


def main():
    saldo = 0.0
    extrato = ""
    numero_saques = 0

    while True:
        opcao = exibir_menu()

        if opcao == "d":
            saldo, extrato = depositar(saldo, extrato)

        elif opcao == "s":
            saldo, extrato, numero_saques = sacar(saldo, extrato, numero_saques)

        elif opcao == "e":
            exibir_extrato(saldo, extrato)

        elif opcao == "q":
            print("\n✅ Obrigado por usar nosso sistema bancário. Até logo!")
            break

        else:
            print("❌ Opção inválida! Tente novamente.")


if __name__ == "__main__":
    main()

