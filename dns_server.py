'''
Implementation of DNS server
'''

import random as rand
import socket
import threading
import sys
import select as s
import dnslib as dns
import pickle
from utils import *

CMD_LIST_SUBDOMAINS = 'ls'
CMD_LIST_HOSTS = 'lh'

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class DNSserver():
    '''
    A server must register either a Host process or a Server process.
    The lookup is found is implemented by the RESOLVER.
    '''

    def __init__(self) -> None:
        self.ip = 'localhost' # restringe para processos internos por eficiencia
        self.domain = input('Entre com o nome do domínio (para root use "."): ')
        if self.domain != '.':
            # address 127.0.0.1:53000 is reserved for the root server
            self.port = rand.randint(53001, 53999)

            # as this runs locally, 'localhost' is set, but
            # if ran on different machines and input would be shown
            parent_ip = 'localhost' # input('Entre com o endereço IPv4 do server pai: ')
            parent_port = input('Entre com a porta do server pai: ')
            self.parent_addr = (parent_ip, int(parent_port))
        else:
            # root address must be known
            self.port = 53000
            self.parent_addr = None
            self.full_domain = self.domain

        # dict mapping hosts and servers to their respective ips
        self.hosts = {}
        self.subdomains = {}

        # starts the server socket using UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # select entry points
        self.entry_points = [self.socket, sys.stdin]

        self.lock = threading.Lock()
        pass

    def __enter__(self):
        return self

    def start(self):
        self.socket.bind((self.ip, self.port))

        #self.socket.setblocking(False)
        try:
            if self.parent_addr is not None:
                self.register_in_parent()
            self.display_server_info()
            while True:
                r, w, x = s.select(self.entry_points, [], [])

                for ready in r:
                    if ready == self.socket:
                        msg, sender_addr = self.receive_message()

                        if type(msg) == RegisterMsg:
                            reg = self.handle_register(msg, sender_addr)
                            reg.join()
                        elif type(msg) == dns.DNSRecord:
                            response = self.generate_response(msg)                           
                            self.socket.sendto(pickle.dumps(response), sender_addr)
                        else:
                            print(f'Servidor recebeu de {sender_addr} uma mensagem inesperada')
                            
                    elif ready == sys.stdin:
                        cmd = input()
                        print('Server> ' + cmd)
                        if cmd == CMD_END:
                            self.socket.close()
                            print('Servidor encerrado! Até logo!')
                            exit()
                        elif cmd == CMD_LIST_HOSTS:
                            print(self.hosts)
                        elif cmd == CMD_LIST_SUBDOMAINS:
                            print(self.subdomains)
                        
        except Exception as e:
            print('Servidor encerrado.', e)
        pass
    
    def register_in_parent(self):
        '''Sends a RegisterMsg to the server parent and receives the answer.
        If the register is not succeeded, the Server will be ended.
        '''
        data = RegisterMsg(TypeEnum.SERVER, self.domain)
        self.socket.sendto(pickle.dumps(data), self.parent_addr)
        try:
            self.socket.settimeout(TIMEOUT)
            data, _ = self.socket.recvfrom(BUFSIZE)
            self.socket.settimeout(None)
            result: RegisterResultMsg = pickle.loads(data)
            if not result.success:
                print('Não foi possível registrar o server.')
                if result.error_text:
                    print(result.error_text)
                print('Encerrando execução...')
                exit()
            else:
                self.full_domain = result.full_domain
                print(f'Server registrado com sucesso!')
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

    def display_server_info(self):
        '''Display where the server is hosted and his domain name.'''
        print('\n===================================================')
        print(f'Server hospedado em: "{self.ip}:{self.port}".')
        print(f'Domínio: {self.domain}')
        print(f'Domínio completo: {self.full_domain}')
        print('===================================================\n')

    def receive_message(self):
        '''Receives a message and converts the bytes.'''
        data, addr = self.socket.recvfrom(BUFSIZE)
        data = pickle.loads(data)

        return data, addr

    @threaded
    def handle_register(self, msg: RegisterMsg, addr):
        '''Given a RegisterMsg, register the server/host as child and sends back a 
        message informing whether the register was succeeded. Also sends back the 
        full domain of the new server/host.
        '''
        self.lock.acquire()
        if msg.type == TypeEnum.HOST:
            self.hosts[msg.name] = addr[1]
        elif msg.type == TypeEnum.SERVER:
            self.subdomains[msg.name] = addr[1]
        self.lock.release()

        # se o server for o root, não deve concatenar nada ao domínio do filho
        # se não for o root, concaneta o nome do filho com o domínio completo do server
        full_domain = msg.name + ('' if self.domain == '.' else '.'+self.full_domain)
        result = RegisterResultMsg(True, full_domain=full_domain)
        self.socket.sendto(pickle.dumps(result), addr)

        print(f'Novo {msg.type.value} registrado:')
        print(f'{msg.name} => {addr}')

    def generate_response(self, msg):
        # !! if running on different machines, use rdata=dns.A(question) !!
        question = str(msg.questions[0]).replace(';', '')
        # !!!encodes the port in IP format (USE ONLY IF RUNNING ON LOCALHOSTS)!!!
        q_parts = question.split('.')

        name = q_parts[-2] # gets the next server/host

        if name in self.hosts:
            return self.create_DNS_record_response(question, self.hosts.get(name))
        elif name in self.subdomains:
            return self.create_DNS_record_response(question, self.subdomains.get(name))
        else:
            return SubdomainNotFoundMsg(name)

    def create_DNS_record_response(self, question, addr):
        '''Creates a DNSRecord instance with the given address and question'''
        str_addr = str(addr)
        address = str_addr[0] + str_addr[1] + '.' + str_addr[2] + '.' + str_addr[3] + '.' + str_addr[4]

        # treat client with response
        return dns.DNSRecord(
            dns.DNSHeader(qr=1,aa=1,ra=0),
            q=dns.DNSQuestion(question),
            a=dns.RR(question, rdata=dns.A(address))
        )    


    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self.socket.close()
        pass

    def __del__(self) -> None:
        self.socket.close()
        pass

def main():

    with DNSserver() as server:
        server.start()

if __name__ == '__main__':
    main()
