import socket
import random as rand
from dns_resolver import DNSresolver as Resolver

CMD_END = 'end'

def read_input(hint = '>'):
    '''Reads the input unitl it's a valid input.
    '''
    while True:
        text = input(hint)
        if len(text) > 0:
            return text

class Client():
    '''The client provides the user interface. It is responsible for 
    reading the user questions, sending it to the resolver and presenting
    the answer to the user.
    '''
    
    def __init__(self):
        self.ip = 'localhost'
        self.port = rand.randint(50000, 52999)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        print('\n===================================================')
        print(f'Seja bem vindo!')
        print('===================================================\n')

    def resolve(self, question: str):
        resolver = Resolver(question, self.socket)
        return resolver.getHostIP()

    def close(self):
        print('Cliente encerrado! Até logo!')
        self.socket.close()


def main():
    client = Client()
    client.start()

    while True:
        cmd = read_input()
        if cmd == CMD_END:
            client.close()
            break
        else:
            result = client.resolve(cmd)
            print(result)
            print()

if __name__ == '__main__':
    main()