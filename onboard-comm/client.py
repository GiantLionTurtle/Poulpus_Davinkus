import socket

def main(host, port, gcode_file='test.gcode.txt'):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print("Connected to {}".format(host))

        with open(gcode_file, 'r', encoding='utf-8') as f:
            for line in f:
                gcode_line = line.strip()
                if gcode_line:
                    print("Sending: {}".format(gcode_line))
                    s.sendall(gcode_line)
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
        s.sendall('m4thos troll'.encode('utf-8'))
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        s.close()
        print("Connection closed")
    return

if __name__ == '__main__':
    test("rpi_ip_adress", 5000)