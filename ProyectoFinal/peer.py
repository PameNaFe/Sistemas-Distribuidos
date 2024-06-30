import socket
import threading
import os
import sys  # Importa sys para usar sys.exit()

class Peer:
    def __init__(self, id, host='127.0.0.1', port=5001, tracker_host='192.168.1.74', tracker_port=5000): 
        # tracker_host debe coincidir con la dirección del tracker, host es la ip que tenga el otro nodo
        self.id = id
        self.host = host
        self.port = port + id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.files = {}  # {filename: [is_complete, progress]}
        self.peers = []
        self.is_seeder = False

    def connect_to_tracker(self):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        tracker.send(b"list")
        files = tracker.recv(1024).decode()
        self.peers = eval(files)
        tracker.close()

    def register_file_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        
        # Informar al tracker sobre el archivo compartido
        message = f"share {filename} {self.host} {self.port} {progress}"
        tracker.send(message.encode())
        
        # Actualizar lista de peers desde el tracker
        peers = tracker.recv(1024).decode()
        self.peers = eval(peers)
        tracker.close()

    def register_download_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        
        # Informar al tracker sobre el progreso de la descarga
        message = f"download {filename} {self.host} {self.port} {progress}"
        tracker.send(message.encode())
        
        # Actualizar lista de peers desde el tracker
        peers = tracker.recv(1024).decode()
        self.peers = eval(peers)
        tracker.close()

    def start(self):
        threading.Thread(target=self.server).start()
        self.connect_to_tracker()
        self.client()

    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Peer {self.id} listening on {self.host}:{self.port}")

        while True:
            client, address = server.accept()
            filename = client.recv(1024).decode()
            if filename in self.files and self.files[filename][0]:
                client.send(b'ACK')
                with open(filename, 'rb') as f:
                    client.sendfile(f)
            client.close()

    def client(self):
        while True:
            print(f"\nBienvenido, Peer {self.id}")
            print("1. Listado del tracker")
            print("2. Compartir archivo ('share [nombre_archivo]')")
            print("3. Descargar archivo ('download [nombre_archivo]')")
            print("4. Cancelar acción ('cancel [nombre_archivo]')")
            print("5. Salir")
            command = input("Selecciona una opción: ")
            
            if command == '1':
                self.list_files()
            elif command.startswith('share '):
                filename = command.split(' ')[1]
                self.share_file(filename)
            elif command.startswith('download '):
                filename = command.split(' ')[1]
                self.files[filename] = [False, 0]
                threading.Thread(target=self.download_file, args=(filename,)).start()
            elif command.startswith('cancel '):
                filename = command.split(' ')[1]
                self.cancel_action(filename)
            elif command == '5':
                print(f"Peer {self.id} desconectado. ¡Hasta luego!")
                sys.exit()  # Sale del programa
            else:
                print("Comando inválido.")

    def list_files(self):
        self.connect_to_tracker()
        files_list = "\n".join(self.peers)  # Agrega un salto de línea entre cada archivo
        print("Archivos en el tracker:\n", files_list)

    def share_file(self, filename):
        if os.path.exists(filename):
            self.files[filename] = [True, 100]
            self.is_seeder = True
            print(f"Peer {self.id} está compartiendo {filename}")
            
            # Registrar archivo con el tracker
            self.register_file_with_tracker(filename, 100)
            print(f"Archivo compartido con éxito.")
        else:
            print(f"El archivo {filename} no existe.")

    def download_file(self, filename):
        for peer_host, peer_port, is_complete, progress in self.peers.get(filename, []):
            if peer_host == self.host and peer_port == self.port:
                continue
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((peer_host, peer_port))
                client.send(filename.encode())
                response = client.recv(1024)
                if response == b'ACK':
                    with open(f"{filename}_part_{self.id}", 'wb') as f:
                        while True:
                            data = client.recv(1024)
                            if not data:
                                break
                            f.write(data)
                            self.files[filename][1] += len(data)
                            percentage = (self.files[filename][1] / os.path.getsize(filename)) * 100
                            print(f"Descargando {filename}: {percentage:.2f}%")
                            self.register_download_with_tracker(filename, int(percentage))
                    self.files[filename] = [True, 100]
                    print(f"Peer {self.id} completó la descarga de {filename}")
                    client.close()
                    break
            except Exception as e:
                print(f"Falló la descarga desde {peer_host}:{peer_port}, error: {e}")
                continue

    def cancel_action(self, filename):
        if filename in self.files:
            del self.files[filename]
            print(f"Cancelada la acción de compartir/descargar de {filename}")
        else:
            print(f"El archivo {filename} no se está compartiendo ni descargando.")

if __name__ == "__main__":
    peer_id = int(input("Ingresa el ID del peer: "))
    peer = Peer(peer_id)
    peer.start()
