import socket
import os

def main(host, port, gcode_file):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print("Connected to {}".format(host))

        with open(gcode_file, 'r', encoding='utf-8') as f:
            for line in f:
                gcode_line = line.strip()
                if gcode_line:
                    print("Sending: {}".format(gcode_line))
                    s.sendall(gcode_line.encode('utf-8') + b'\n')
                    print("Sent: {}".format(gcode_line))
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        s.close()
        print("Connection closed")
    return

def test(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print("Connected to {}".format(host))
        s.sendall('Hello World!'.encode('utf-8'))
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        s.close()
        print("Connection closed")
    return

if __name__ == '__main__':
    g_code_file_path = os.path.abspath("/home/vidieu/Documents/School/S4/Projet/gcode.txt")
    main("rpi_adress", 5000, g_code_file_path)