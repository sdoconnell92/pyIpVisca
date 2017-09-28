import socket
import multiprocessing
import time
import datetime
import logging


def send_udp_packet(ip, port, message):

    # Initialize socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    d = datetime.datetime.now()
    currentTime = str(d.minute) + str(d.second) + ":" + str(d.microsecond)
    print("{" + currentTime + "} UDP Packet to: " + ip + ":" + str(port) + " |msg|: " + message)
    logging.debug("{" + currentTime + "} UDP Packet to: " + ip + ":" + str(port) + " |msg|: " + message)
    try:
        sock.sendto(message.decode('hex'), (ip, port))
    except TypeError:
        print("ERROR: Invalid hex message.")
        print("INFO: Send Aborted")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")


def wait_for_cam_udp_packet():

    ip = '192.168.0.74'
    port = 52381

    # Set up the socket to receive
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((ip, port))

    # Start Listening
    print("Listening on: " + ip + ":" + str(port))
    while True:
        # grab any messages
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

    print("Recieved Message from camera: " + )

if __name__ == '__main__':
    logging.basicConfig(filename="logfilepython.log", level=logging.DEBUG)
    logging.debug('Starting Python Program')
