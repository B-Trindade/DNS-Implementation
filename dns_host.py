import socket
import sys
from select import select
import random as rand
import pickle
from utils import *

class DNSHost():
    def __init__(self) -> None:
        self.ip = 'localhost'
        self.port = rand.randint(53001, 53999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.parent_addr = None
        self.name: str = None
        self.full_domain: str = None

    def start(self):
        self.sock.bind((self.ip, self.port))
        self.register_host()
        self.display_host_info()

    def register_host(self):
        self.get_host_info()
        data = RegisterMsg(TypeEnum.HOST, self.name)
        self.sock.sendto(pickle.dumps(data), self.parent_addr)
        try:
            self.sock.settimeout(TIMEOUT)
            data, _ = self.sock.recvfrom(BUFSIZE)
            self.sock.settimeout(None)
            result: RegisterResultMsg = pickle.loads(data)
            if not result.success:
                print('Não foi possível registrar o host.')
                if result.error_text:
                    print(result.error_text)
                print('Encerrando execução...')
                exit()
            else:
                self.full_domain = result.full_domain
                print('Host registrado com sucesso!')
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

    def display_host_info(self):
        print('\n===================================================')
        print(f'Host hospedado em: "{self.ip}:{self.port}".')
        print(f'Domínio: {self.name}')
        print(f'Domínio completo: {self.full_domain}')
        print('===================================================\n')

    def get_host_info(self):
        self.name = input('Entre com o nome do domínio: ')
        parent_ip = 'localhost' #input('IP do servidor:')
        parent_port = input('Entre com a porta do server pai: ')
        self.parent_addr = (parent_ip, int(parent_port))

    def handle_ping(self):
        data, addr = self.sock.recvfrom(BUFSIZE)
        msg: PingMsg = pickle.loads(data)

        if type(msg) != PingMsg:
            print(f'Host recebeu de {addr} mensagem que não é ping.')
        else:
            print(msg)
            response = PingResultMsg(msg.name == self.full_domain)
            self.sock.sendto(pickle.dumps(response), addr)

    def close(self):
        print('Host encerrado! Até logo!')
        self.sock.close()

def main():
    host = DNSHost()
    host.start()

    entry_points = [host.sock, sys.stdin]


    while True:
        r, w, x = select(entry_points, [], [])
        for ready in r:
            if ready == host.sock:
                host.handle_ping()
            elif ready == sys.stdin:
                cmd = input()
                if cmd == CMD_END:
                    host.close()
                    exit()

if __name__ == '__main__':
    main()