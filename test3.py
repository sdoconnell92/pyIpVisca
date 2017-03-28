import socket


def wait_for_udp_packet(udp_ip, udp_port):

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    import time
    millis = int(round(time.time() * 1000))
    print(millis)
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        millis = int(round(time.time() * 1000))
        print("received message:|(" + str(millis) + ")| ", data )


ip = "192.168.0.110"
port = 52381

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

clear_mes = b'\x01\x00\x00\x00\xff\xff\xff\xff'
go_home = b'\x01\x00\x00\x05\x00\x00\x00\x00\x81\x01\x06\x04\xff'


sock.sendto(clear_mes_2, (ip, port))
sock.sendto(go_home_2, (ip, port))

wait_for_udp_packet("192.168.0.73", 52381)