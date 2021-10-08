import socket
import sys
from select import select
import random as rand
import pickle
from utils import *
import dnslib as dns


CMD_END = 'end'
TIMEOUT = 3.0

class DNSHost():
    def __init__(self) -> None:
        self.ip = 'localhost'
        self.port = rand.randint(53001, 53999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.parent_addr = None
        self.name: str = None

    def start(self):
        self.sock.bind((self.ip, self.port))
        print(f'Host started\nIP: {self.ip}\nPort:{self.port}')

    def register_host(self):
        self.get_host_info()
        data = RegisterMsg(TypeEnum.HOST, self.name)
        self.sock.sendto(pickle.dumps(data), self.parent_addr)
        try:
            self.sock.settimeout(TIMEOUT)
            data, _ = self.sock.recvfrom(1024)
            self.sock.settimeout(None)
            result = pickle.loads(data)
            if not result.success:
                print('Não foi possível registrar o host.')
                if result.error_text:
                    print(result.error_text)
                print('Encerrando execução...')
                exit()
            else:
                print(f'Host "{self.name}" registrado com sucesso!')
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

    def get_host_info(self):
        self.name = input('Nome do host:')
        parent_ip = 'localhost' #input('IP do servidor:')
        parent_port = input('Porta do servidor:')
        self.parent_addr = (parent_ip, int(parent_port))

    def handle_ping(self):
        '''Recebe a mensagem de ping e envia uma mensagem de volta, 
        indicando se é de fato o host que foi pingado.
        '''
        data, addr = self.sock.recvfrom(4096)
        msg = pickle.loads(data)
        port = str(self.port)

        question = str(msg.questions[0]).replace(';', '')
        address = f'{port[0]}{port[1]}.{port[2]}.{port[3]}.{port[4]}'

        response = dns.DNSRecord(
            dns.DNSHeader(qr=1,aa=1,ra=0),
            q=dns.DNSQuestion(question),
            a=dns.RR(question, rdata=dns.A(address))
        )      

        self.sock.sendto(pickle.dumps(response), addr)

    def close(self):
        print('Host encerrado! Até logo!')
        self.sock.close()

def main():
    host = DNSHost()
    host.start()
    host.register_host()

    entry_points = [host.sock, sys.stdin]

    r, w, x = select(entry_points, [], [])

    while True:
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