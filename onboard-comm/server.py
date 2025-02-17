import socket

def main(host,port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"[*] Listening as {host}:{port}")

    client_socket, client_address = s.accept()
    print(f"[*] Connection from {client_address}")

    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        print(f"[*] Data from client: {data}")
        gcode_line = data.strip()
        print(f"Received G-code: {gcode_line}")
        #If want to add later a confirmation message
        #client_socket.sendall("Received")
    client_socket.close()
    s.close()

if __name__ == "__main__":
    main("0.0.0.0",5000)
