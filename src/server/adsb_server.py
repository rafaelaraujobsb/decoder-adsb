import socket
import time
from subprocess import check_output
from pool.worker import messages

class Server:
    def __init__(self, port, host=''):
        self.host = host
        self.port = port  # porta que será executado o socket

        # AF_INET: indica o uso de IPv4
        # SOCK_DGRAM: indica que o socket será usado com UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))  # seta as configurações de porta e host

        # pegar ip do servidor
        self.ip = check_output(['hostname', '-I']).decode().split()[0]

        print('Pressione CTRL+C para encerrar')
        print('\nIP: %s\nPorta: %d' % (self.ip, self.port))
        print('\n[+] Servidor ON\n')

    def listen(self):
        # ativa o servidor para receber conexões e indica quantas conexões
        # não aceitas devem ser recebidas para não permitir novas conexões
        self.sock.listen(1)

        while True:
            try:
                client, address = self.sock.accept()
            except:
                self.sock.close()
                print('\n[+] Servidor OFF')
                break

            client.settimeout(60)  # tempo de inatividade

            print('Cliente conectado ', address)

            while True:
                data = client.recv(1024)  # recebe os dados enviados

                if not data:
                    break

                # captura a resposta
                timestamp = int(time.time())
                data = str(data.decode())

                messages.put((data, timestamp))

            print('Cliente desconectado ', address)
            client.close()


def start_server(port=1254):
    Server(port).listen()
