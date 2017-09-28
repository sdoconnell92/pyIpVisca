import multiprocessing
import socket
import time


def udp_listen(udp_ip, udp_port):

    print("Listening on:" + udp_ip + ":" + str(udp_port))

    # Set up socket
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("recieved MEssage: ", data.encode('hex'))

if __name__ == '__main__':
    udp_listen('192.168.0.100', 52381)
