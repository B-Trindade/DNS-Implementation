import socket
import sys
from select import select
import random as rand
import pickle
from utils import *

HOST_IP = 'localhost'
HOST_PORT = rand.randint(53000, 53999)
CMD_END = 'end'
TIMEOUT = 3.0

def get_host_info():
    name = input('Nome do host:')
    parent_ip = 'localhost' #input('IP do servidor:')
    parent_port = input('Porta do servidor:')
    return name, (parent_ip, int(parent_port))

def create_host_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST_IP, HOST_PORT))
    print(f'Host started\nIP: {HOST_IP}\nPort:{HOST_PORT}')
    return sock

def register_host(host_sock):
    host_name, server_addr = get_host_info()
    data = RegisterMsg(TypeEnum.HOST, host_name)
    host_sock.sendto(pickle.dumps(data), server_addr)
    try:
        host_sock.settimeout(TIMEOUT)
        data, addr = host_sock.recvfrom(1024)
        host_sock.settimeout(None)
        result = pickle.loads(data)
        if not result.success:
            print('Não foi possível registrar o host.')
            if result.error_text:
                print(result.error_text)
            print('Encerrando execução...')
            exit()
        else:
            print(f'Host "{host_name}" registrado com sucesso!')
    except socket.timeout:
        print('O servidor não respondeu dentro do tempo esperado. '
            'Tente novamente mais tarde.\n'
            'Encerrando execução...')
        exit()
    except Exception as e:
        print('Algo inesperado ocorreu e não foi possível registrar o host.')
        print(e)
        print('Encerrando execução...')
        exit()

def main():
    host_sock = create_host_socket()

    register_host(host_sock)

    entry_points = [host_sock, sys.stdin]

    r, w, x = select(entry_points, [], [])

    while True:
        for ready in r:
            if ready == host_sock:
                # é um ping, responder
                data, addr = host_sock.recvfrom(1024)
                msg = pickle.loads(data)
                print(f'{addr}: {msg}')
            elif ready == sys.stdin:
                cmd = input()
                if cmd == CMD_END:
                    host_sock.close()
                    exit()

    

if __name__ == '__main__':
    main()