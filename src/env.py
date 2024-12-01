# -*- coding: utf-8 -*-

# Imports
import time
import random
from datetime import datetime
import sys
import threading
sys.dont_write_bytecode = True
import cPickle as pickle
import os, time, socket, struct
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from utils import *

# Constants
NACCEPTORS = 5
NREPLICAS = 3
NLEADERS = 2
NREQUESTS = 10

# Environment class
class Env:
    def __init__(self, dist):
        self.dist = False
        if dist != 1: self.dist=True
        if self.dist:
            self.available_addresses =  self.generate_ports('localhost', 10000*int(sys.argv[2])+10000, 10000*int(sys.argv[2])+11111)
        else:
            self.available_addresses =  self.generate_ports('localhost', 10000, 11111)
        self.procs = {}
        self.proc_addresses = {}
        self.config = Config([], [], [])
        self.c = 0
        self.perf = 0

    def get_network_address(self):
        return self.available_addresses.pop(0) if self.available_addresses else None
    
    def generate_ports(self, host, start_port, end_port):
        return [(host, port) for port in range(start_port, end_port + 1)]

    def release_network_address(self, address):
        self.available_addresses.append(address)

    def sendMessage(self, dst, msg):
        if dst in self.proc_addresses:
            host, port = self.proc_addresses[dst]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 0)) 
        try:
            s.connect((host, port))
            data = pickle.dumps(msg, protocol=pickle.HIGHEST_PROTOCOL)
            s.sendall(struct.pack('!I', len(data)) + data)
        except Exception as e:
            print("Failed to send message:", e)
        finally:
            s.close()

    def addProc(self, proc):
        self.procs[proc.id] = proc
        self.proc_addresses[proc.id] = (proc.host, proc.port)
        proc.start()

    def removeProc(self, pid):
        if pid in self.procs:
            del self.procs[pid]
            del self.proc_addresses[pid]

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)

    # Create default configuration
    def create_default(self):
        print("Using default configuration\n\n")
        for i in range(NREPLICAS):
            pid = "replica %d" % i
            host, port = self.get_network_address()
            Replica(self, pid, self.config, host, port)
            self.config.replicas.append(pid)
        for i in range(NACCEPTORS):
            pid = "acceptor %d.%d" % (self.c,i)
            host, port = self.get_network_address()
            Acceptor(self, pid, host, port)
            self.config.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (self.c,i)
            host, port = self.get_network_address()
            Leader(self, pid, self.config, host, port)
            self.config.leaders.append(pid)
  
    # Create custom configuration
    def create_custom(self):
        print("Using custom configuration\n\n")
        try:
            file = open("..\config\\"+sys.argv[1], 'r')
            for line in file:
                parts = line.split(" ")
                if line.startswith("REPLICA"):
                    pid = "replica %d" % int(parts[1])
                    self.config.replicas.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "REPLICA" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Replica(self, pid, self.config, host, int(port))
                elif line.startswith("ACCEPTOR"):
                    pid = "acceptor %d" % (int(parts[1]))
                    self.config.acceptors.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "ACCEPTOR" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Acceptor(self, pid, host, int(port))
                elif line.startswith("LEADER"):
                    pid = "leader %d" % (int(parts[1]))
                    self.config.leaders.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "LEADER" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Leader(self, pid, self.config, host, int(port))
        except Exception as e:
            print(e)
            self._graceexit()
        finally:
            file.close()
            
    def process_deposit(self, pid, input, thread_id, request_id):
        # Código que será executado em cada requisição
        cmd = Command(pid,0,input+"#%d.%d" % (int(thread_id),int(request_id)))
        print("pid: ", pid)
        if self.dist:
            for key, val in self.proc_addresses.items():
                if key.startswith("replica"):
                    self.sendMessage(key, RequestMessage(pid, cmd))
    
    # Run environment
    def run(self):
        print("\n")
        while True:
            try:
                input = raw_input("\nInput: ")
                
                # Exit
                if input == "exit":
                    self._graceexit()
                
                # New client
                elif input.startswith("newclient"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print("Usage: newclient <client_name> <client_id>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        print("gerou comando")
                        if self.dist:
                            print("a")
                            for key, val in self.proc_addresses.items():
                                print("b")
                                if key.startswith("replica"):
                                    print("mandou pra uma replica")
                                    print(val)
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                
                # New account   
                elif input.startswith("newaccount"):
                    parts = input.split(" ")
                    if len(parts) != 3 and len(parts) != 2:
                        print("Usage: newaccount <client_id> <account_id>")
                        print("Usage: newaccount <account_id>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                
                # Add account    
                elif input.startswith("addaccount"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print("Usage: addaccount <client_id> <account_id>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                
                # Balance   
                elif input.startswith("balance"):
                    parts = input.split(" ")
                    if len(parts) != 2 and len(parts) != 3:
                        print ("Usage: balance <client_id> <account_id>")
                        print ("Usage: balance <client_id>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                
                # Deposit
                elif input.startswith("deposit"):
                    parts = input.split(" ")
                    if len(parts) < 3:
                        print("Usage: deposit <account_id> <amount>")
                    elif len(parts) == 3:
                        pid = "client %d.%d" % (self.c,self.perf)
                        print("pid: ", pid)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                    elif len(parts) == 5:
                        #Usage: deposit <account_id> <amount> <number of threads> <number of requests per thread>
                        try:
                            account_id = parts[1]
                            amount = float(parts[2])
                            num_threads = int(parts[3])
                            requests_per_thread = int(parts[4])
                        except ValueError:
                            print("Invalid input. Ensure amount is a number and the thread/request counts are integers.")
                            return
                        
                        threads = []
                        media_vazao_thread = []
                        media_temp_resp_thread = []
                        timestamps = {i: [] for i in range(num_threads)}  # Dicionário para salvar os timestamps por thread
                        
                        def thread_task(thread_id):
                            response_times = []
                            for request_id in range(requests_per_thread):
                                # random_sleep_time = random.uniform(0, 5)
                                # time.sleep(random_sleep_time)
                                start_time = datetime.now()
                                timestamps[thread_id].append((request_id, start_time))
                                pid = "client %d.%d" % (int(thread_id), int(request_id))
                                self.process_deposit(pid, "deposit %d %d" % (int(account_id), int(amount)), thread_id, request_id)
                                pidSearch = pid.split(" ")[1]
                                last_position = 1
                                while True:
                                    with open("../logs/replica_0", "r") as log_file:
                                        # Move para a última posição lida
                                        log_file.seek(last_position)

                                        # Lê apenas as novas linhas
                                        new_lines = log_file.readlines()
                                        last_position = log_file.tell()  # Atualiza a posição no arquivo
                                        
                                        # Verifica se o PID está nas novas linhas
                                        if any(pidSearch in line for line in new_lines):
                                            end_time = datetime.now()
                                            response_time = (end_time - start_time).total_seconds()
                                            response_times.append(response_time)
                                            # PID encontrado no log, prosseguir com a próxima requisição
                                            break

                                    # Pequeno intervalo antes de checar novamente
                                    time.sleep(0.1)
                                
                            # Calcula o tempo médio de resposta da thread
                            average_response_time = sum(response_times) / len(response_times)
                            media_temp_resp_thread.append(average_response_time)
                            
                            average_req_por_segundos = len(response_times) / sum(response_times) 
                            media_vazao_thread.append(average_req_por_segundos)
                               

                            # Loga o tempo médio da thread em um arquivo
                            with open("../logs/thread_response_times.log", "a") as response_log_file:
                                
                                response_log_file.write("Thread %d: Tempo médio de latência = %.2f segundos\n" % (thread_id, average_response_time))
                                response_log_file.write("Thread %d: Requisições por segundo = %.2f segundos\n" % (thread_id, average_req_por_segundos))
                                    
                        for i in range(num_threads):
                            thread = threading.Thread(target=thread_task, args=(i,))
                            threads.append(thread)

                        process_start_time = datetime.now()
                        # Inicia as threads
                        for thread in threads:
                            thread.start()

                        # Espera todas as threads terminarem
                        for thread in threads:
                            thread.join()
                            
                        process_end_time = datetime.now()
                        total_time = (process_end_time - process_start_time).total_seconds()
                        
                        total_requests = num_threads * requests_per_thread
                        throughput = total_requests / total_time
                        
                        vazao_total = sum(media_vazao_thread)
                        latencia_media_total = sum(media_temp_resp_thread) / num_threads

                        with open("../logs/thread_response_times.log", "a") as summary_log_file:
                            summary_log_file.write("Tempo total do processo: %.2f segundos\n" % total_time)
                            #summary_log_file.write("Vazão total: %.2f requisições por segundo\n" % throughput)
                            summary_log_file.write("Vazão total: %.2f requisições por segundo\n" % vazao_total)
                            summary_log_file.write("Média latência total: %.2f segundos\n" % latencia_media_total)
                            
                        # Exibe os tempos de execução para cada requisição
                        # for thread_id, times in timestamps.items():
                        #     print("\nThread: ", thread_id)
                        #     for request_id, start_time in times:
                        #         print("  Request ", request_id, " started at ", start_time)
                # Withdraw
                elif input.startswith("withdraw"):
                    parts = input.split(" ")
                    if len(parts) != 4:
                        print("Usage: withdraw <client_id> <account_id> <amount>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Transfer
                elif input.startswith("transfer"):
                    parts = input.split(" ")
                    if len(parts) != 5:
                        print("Usage: transfer <client_id> <from_account_id> <to_account_id> <amount>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses.items():
                                if key.startswith("replica"):
                                    self.sendMessage(key,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)
                        
                # Fail
                elif input.startswith("fail"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print("Usage: fail <func> <id>")
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            #for key, val in self.proc_addresses:
                                #if key.startswith("replica"):
                                    #self.sendMessage(val,RequestMessage(pid,cmd))
                                    pass
                        else:
                            if parts[1] == "replica":
                                for r in self.config.replicas:
                                    self.sendMessage(r,RequestMessage(pid,cmd))
                            if parts[1] == "acceptor":
                                for r in self.config.acceptors:
                                    self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Create new configuration
                elif input == "reconfig":
                    self.c+=1
                    self.config = Config(self.config.replicas, [], [])
                    for i in range(NACCEPTORS):
                        pid = "acceptor %d.%d" % (self.c,i)
                        host, port = self.get_network_address()
                        Acceptor(self, pid, host, port)
                        self.config.acceptors.append(pid)
                    for i in range(NLEADERS):
                        pid = "leader %d.%d" % (self.c,i)
                        host, port = self.get_network_address()
                        Leader(self, pid, self.config, host, port)
                        self.config.leaders.append(pid)
                    for r in self.config.replicas:
                        pid = "master %d.%d" % (self.c,i)
                        cmd = ReconfigCommand(pid,0,str(self.config))
                        self.sendMessage(r, RequestMessage(pid, cmd))
                        time.sleep(1)
                    for i in range(WINDOW-1):
                        pid = "master %d.%d" % (self.c,i)
                    for r in self.config.replicas:
                        cmd = Command(pid,0,"operation noop")
                        self.sendMessage(r, RequestMessage(pid, cmd))
                        time.sleep(1)
                    self.perf=-1
                
                # Default
                else:
                    print("Unknown command")
                    self.perf=-1
                self.perf+=1
            
            except Exception as e:
                print(e)
                self._graceexit()

# Main
def main():
  # Create environment and check arguments
    e = Env(len(os.sys.argv))
    if len(os.sys.argv) == 1:
        e.create_default()
        time.sleep(1)
    elif len(os.sys.argv) == 4:
        e.create_custom()
        time.sleep(5)
    else:
        print("Usage: env.py")
        print("Usage: env.py <config_file> <id> <function>")
        os._exit(1)
    
    # Reset log files
    for f in os.listdir("../logs"):
        path = os.path.join("../logs", f)
        if os.path.isfile(path):
            os.remove(path)
                     
    # Run environment
    e.run()

# Main call
if __name__=='__main__':
    main()