#!/bin/bash

echo "Iniciando comandos..."

start "ACCEPTOR0" cmd /k "python env.py config0 0 ACCEPTOR"
start "ACCEPTOR1" cmd /k "python env.py config0 1 ACCEPTOR"
start "ACCEPTOR2" cmd /k "python env.py config0 2 ACCEPTOR"
start "ACCEPTOR3" cmd /k "python env.py config0 3 ACCEPTOR"
start "ACCEPTOR4" cmd /k "python env.py config0 4 ACCEPTOR"
start "LEADER0" cmd /k "python env.py config0 0 LEADER"
start "LEADER1" cmd /k "python env.py config0 1 LEADER"
start "LEADER2" cmd /k "python env.py config0 2 LEADER"
start "REPLICA0" cmd /k "python env.py config0 0 REPLICA"
start "REPLICA1" cmd /k "python env.py config0 1 REPLICA"
start "REPLICA2" cmd /k "python env.py config0 2 REPLICA"

echo "Todos os comandos foram concluídos!"