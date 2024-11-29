COMANDOS PARA ABRIR O CONSOLE EM NOVA JANELA:

- start "ACCEPTOR0" cmd /k "python env.py config0 0 ACCEPTOR"
- start "ACCEPTOR1" cmd /k "python env.py config0 1 ACCEPTOR"
- start "LEADER0" cmd /k "python env.py config0 0 LEADER"
- start "REPLICA0" cmd /k "python env.py config0 0 REPLICA"
- start "REPLICA1" cmd /k "python env.py config0 1 REPLICA"

COMANDOS CASO QUEIRA ABRIR VARIOS CMDS UM DO LADO DO OUTRO:

- python env.py config0 0 ACCEPTOR
- python env.py config0 1 ACCEPTOR
- python env.py config0 0 LEADER
- python env.py config0 0 REPLICA
- python env.py config0 1 REPLICA

DEPOIS DE USAR UM DESSES JEITOS PARA STARTAR OS PROCESSOS EXISTE UMA LISTA DE COMANDOS QUE PODE SER DADA NO TERMINAL DE ALGUM DELES, TAIS COMANDOS
DISPARAM AS REQUISICOES E SAO POSTOS NO LOG.

COMANDOS:

newclient <client_name> <client_id>

newaccount <client_id> <account_id>

deposit <account_id> <amount>

balance <client_id> <account_id>

withdraw <client_id> <account_id> <amount>

transfer <client_id> <from_account_id> <to_account_id> <amount>

OBS: A QUANTIDADE DE PROCESSOS CRIADAS TEM QUE SER EXATAMENTE O QUE ESTA NO CONFIG0, CASO QUEIRA ADICIONAR MAIS PROCESSOS ADICIONE TBM NO CONFIG0
