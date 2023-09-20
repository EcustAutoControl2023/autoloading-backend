import socket


server_ip=('192.168.100.8',8234)
hex_data='0103200200012E0A'
byte_data = bytes.fromhex(hex_data)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def read_sensor_data():
    pass

def read_once():
    int_distance = 0

    try:
        s.connect(server_ip)
        s.sendall(byte_data)
        received_data = s.recv(1024)
        hex_received_data = received_data.hex()
        hex_distance = hex_received_data[6:10]
        int_distance = int(hex_distance,16)
        # print('shuju:', int_distance,'mm')
    finally:
        s.close()
    
    return int_distance