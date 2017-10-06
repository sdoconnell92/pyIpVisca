#!/usr/bin/python2.7

import socket
import multiprocessing
import time
import datetime
import logging

version = "1.03"

clear_message = '01000000ffffffff'


# Function for receiving all udp packets on specified network: for us localhost
def wait_for_udp_packet(udp_ip, udp_port):

    # Set up the socket to receive
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    # Start Listening
    print("Listening on: " + udp_ip + ":" + str(udp_port))
    while True:
        # grab any messages
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        datastr = str(data.encode("hex"))
        d = datetime.datetime.now()
        currentTime = str(d.minute) + str(d.second) + ":" + str(d.microsecond)
        print("{" + currentTime + "} Cam Message From [" + str(addr) + "]: ", data.encode('hex'))
        logging.debug("{" + currentTime + "} Cam Message From [" + str(addr) + "]: " + datastr)


if __name__ == '__main__':
    logging.basicConfig(filename="logfilepython.log", level=logging.DEBUG)
    logging.debug('Starting Python Program')

    print("Version: " + version)

    # Set the address and port to listen on
    comp_ip = "192.168.0.43"
    port = 52381

    # Start the listener
    p = multiprocessing.Process(target=wait_for_udp_packet, args=(comp_ip, port))
    p.start()
    p.join()


