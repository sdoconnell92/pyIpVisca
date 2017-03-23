import socket
import ip_visca_codes as codes


def send_udp_packet(udp_ip, udp_port, message):

    print("UDP target IP:", udp_ip)
    print("UDP target port:", udp_port)
    print("message:", ":".join("{:02x}".format(ord(c)) for c in message) )

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (udp_ip, udp_port))


def wait_for_udp_packet(udp_ip, udp_port):

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    import time
    millis = int(round(time.time() * 1000))
    print millis
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        millis = int(round(time.time() * 1000))
        print("received message:|(" + str(millis) + ")| ", ":".join("{:02x}".format(ord(c)) for c in data) )
        condata = ":".join("{:02x}".format(ord(c)) for c in data)
        concode = ":".join("{:02x}".format(ord(c)) for c in codes.vrep_power_on)
        if condata == concode :
            print("cam is on")
        elif data == codes.vrep_power_off:
            print("cam is off")


