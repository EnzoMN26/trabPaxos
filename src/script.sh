#!/bin/bash

echo "Iniciando comandos..."

gnome-terminal -- bash -c "python env.py config0 0 ACCEPTOR; exec bash"
gnome-terminal -- bash -c "python env.py config0 1 ACCEPTOR; exec bash" 
gnome-terminal -- bash -c "python env.py config0 2 ACCEPTOR; exec bash" 
gnome-terminal -- bash -c "python env.py config0 0 LEADER; exec bash" 
gnome-terminal -- bash -c "python env.py config0 1 LEADER; exec bash" 
gnome-terminal -- bash -c "python env.py config0 2 LEADER; exec bash" 
gnome-terminal -- bash -c "python env.py config0 0 REPLICA; exec bash" 
gnome-terminal -- bash -c "python env.py config0 1 REPLICA; exec bash" 

wait

echo "Todos os comandos foram concluídos!"
