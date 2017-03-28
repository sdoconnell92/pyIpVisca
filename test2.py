import socket
import struct
import binascii

def send_udp_packet(udp_ip, udp_port, message):

    print("UDP target IP:", udp_ip)
    print("UDP target port:", udp_port)
    #print("message:", ":".join("{:02x}".format(ord(c)) for c in message) )
    print ("message:", hex(message))
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (udp_ip, udp_port))


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
        print("received message:|(" + str(millis) + ")| ", ":".join("{:02x}".format(ord(c)) for c in data) )
        condata = ":".join("{:02x}".format(ord(c)) for c in data)
        concode = ":".join("{:02x}".format(ord(c)) for c in codes.vrep_power_on)


clear_seq = "\x01\x00\x00\x00\xff\xff\xff\xff"
go_home = "\x01\x00\x00\x05\x00\x00\x00\x00\x81\x01\x06\x04\xff"
ip = "192.168.0.110"
port = 52381

send_udp_packet(ip, port, clear_seq)
send_udp_packet(ip, port, go_home)
