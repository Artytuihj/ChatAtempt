import socket
import  threading

from numpy import broadcast

clients = []

def handleClient(conn, addr):
    print("Client {} connected".format(addr))
    clients.append(conn)
    try:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            print(f"[{addr}] [{msg.decode()}]")
            broadcast(msg, conn)
    except:
        pass
    finally:
        print(f"[{addr}] [{conn.recv(1024)}]")
        clients.remove(conn)
        conn.close()

def broadcast(msg,sender):
    for client in clients:
        if client != sender:
            try:
                client.send(msg.encode())
            except:
                pass
def main():
    host = "0.0.0.0"
    port = 5555
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print("Server listening on {}:{}".format(host, port))

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handleClient,daemon=True ,args=(conn, addr)).start()

if __name__ == "__main__":
    main()
