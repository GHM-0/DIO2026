
# Teste de Transaction

# 3.
# Conta como Origem de Transferências:
# ◦
# Cenário: Criar uma conta principal e uma ou mais contas secundárias. Realizar uma ou mais transações de TRANSFERENCE onde a conta principal é a account_orig_id.

# Resultado Esperado: O extrato da conta principal deve refletir o saldo final correto (saldo inicial menos o total transferido) e listar todas as transações de saída com seus detalhes (valor, tipo TRANSFERENCE).
# 4.
# Conta como Destino de Transferências:
# ◦
# Cenário: Criar uma conta principal e uma ou mais contas secundárias. Realizar uma ou mais transações de TRANSFERENCE onde a conta principal é a account_dest_id.
# ◦
# Resultado Esperado: O extrato da conta principal deve refletir o saldo final correto (saldo inicial mais o total recebido) e listar todas as transações de entrada com seus detalhes (valor, tipo TRANSFERENCE).
# 5.
# Conta com Múltiplas Transferências (Origem e Destino):
# ◦
# Cenário: Criar uma conta principal e uma ou mais contas secundárias. Realizar uma sequência de transações de TRANSFERENCE onde a conta principal atua tanto como origem quanto como destino.
# ◦
# Resultado Esperado: O extrato da conta principal deve refletir o saldo final correto (saldo inicial - total enviado + total recebido) e listar todas as transações relevantes (saída e entrada) com seus detalhes.
