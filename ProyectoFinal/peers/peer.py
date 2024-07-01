import socket
import pickle
import time 
import threading

class Peer:
    def __init__(self, peer_id, tracker_host='127.0.0.1', tracker_port=5000):
        self.peer_id = peer_id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.shared_files = []
        self.downloaded_files = []
        self.progress = 0
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.tracker_host, self.tracker_port))
        self.register_with_tracker()
        threading.Thread(target=self.update_progress).start()

    def register_with_tracker(self):
        request = {'action': 'register', 'peer_id': self.peer_id}
        self.client.send(pickle.dumps(request))

    def list_files(self):
        request = {'action': 'list_files'}
        self.client.send(pickle.dumps(request))
        response = self.client.recv(4096)
        all_shared_files = pickle.loads(response)
        print("Archivos disponibles en el tracker:")
        for file in all_shared_files:
            print(f"Archivo: {file}")

    def share_file(self):
        file_name = input("Ingresa el nombre del archivo a compartir: ")
        self.shared_files.append(file_name)
        request = {'action': 'share', 'peer_id': self.peer_id, 'file_name': file_name}
        self.client.send(pickle.dumps(request))
        print(f"Archivo {file_name} compartido exitosamente.")

        # Simular progreso de compartición
        for progress in range(0, 101, 10):
            self.progress = progress
            request = {'action': 'progress_update', 'peer_id': self.peer_id, 'progress': self.progress}
            self.client.send(pickle.dumps(request))
            time.sleep(1)  # Simular pausa de 1 segundo entre actualizaciones

    def download_file(self):
        file_name = input("Ingresa el nombre del archivo a descargar: ")
        self.downloaded_files.append(file_name)
        request = {'action': 'download', 'peer_id': self.peer_id, 'file_name': file_name}
        self.client.send(pickle.dumps(request))
        print(f"Iniciando descarga del archivo {file_name}...")

    def update_progress(self):
        while True:
            response = self.client.recv(1024)
            if response:
                progress_update = pickle.loads(response)
                self.progress = progress_update['progress']
                print(f"Progreso de la descarga: {self.progress}%")

    def menu(self):
        while True:
            print("\n--- Menú del Peer ---")
            print("1. Listado de archivos disponibles")
            print("2. Opción de compartir archivo")
            print("3. Opción de descargar archivo")
            print("4. Cancelar acción")
            print("5. Salir del peer")
            choice = input("Elige una opción: ")

            if choice == '1':
                self.list_files()
            elif choice == '2':
                self.share_file()
            elif choice == '3':
                self.download_file()
            elif choice == '4':
                print("Acción cancelada.")
            elif choice == '5':
                self.client.close()
                break
            else:
                print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    peer_id = input("Ingresa el ID del peer: ")
    peer = Peer(peer_id)
    peer.menu()
