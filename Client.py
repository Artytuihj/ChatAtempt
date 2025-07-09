import socket
import threading

def receive(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            print(f"\n[CHAT]{msg}")
        except:
            print("\n[SYS] Connection closed")
            break

def main() -> None:
    server_ip = input("Server IP: ")
    port = 5555
    name = input("Name: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, port))
    print("\n[SYS] Connected")

    threading.Thread(target=receive, args=(sock,),daemon=True).start()

    while True:
        msg = input("\n[SYS] Message: ")
        if msg.lower() == "/quit":
            break
        full_msg = f" [{name}] {msg}"
        sock.send(full_msg.encode())

    sock.close()

if __name__ == "__main__":
    main()
