#!/usr/bin/python2.7

import socket
import multiprocessing
import time


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

        # Try to convert the osc packet to udp
        # If it doesn't succeed due to unicode decode error
        #      This means that it is a message from the camera since it is in hex code
        print("")
        print("Received OSC Message: ", data)
        print("Sending to converter...")
        try:
            convert_osc_udp(data.decode())
        except UnicodeDecodeError:
            pass
            print("Received Cam Message: ", data)

 
def send_udp_packet(udp_ip, udp_port, message):

    # Initialize socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    print("Sending Clear Message to: " + udp_ip + ":" + str(udp_port) + "|msg|: " + clear_message)
    try:
        sock.sendto(clear_message.decode('hex'), (udp_ip, udp_port))
    except TypeError:
        print("ERROR: Type error thrown when trying to send clear message.")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")

    time.sleep(0.01)

    print("Sending UDP Packet to: " + udp_ip + ":" + str(udp_port) + " |msg|: " + message)
    try:
        sock.sendto(message.decode('hex'), (udp_ip, udp_port))
    except TypeError:
        print("ERROR: Invalid hex message.")
        print("INFO: Send Aborted")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")


def convert_osc_udp(message=""):
    # message format: "192.168.0.0::52381::hexmessage<?>"

    # Find where the end of the message is, marked by '<?>'
    x1 = message.find("<?>")
    if x1 != -1:
        # Strip off everything after '<?>' including '<?>
        message = message[:x1]

        # Split the message into each part
        #   The parts are separated by '::'
        message_split = message.split('::')
        if len(message_split) == 3:
            # load the individual parts into variables
            ip = message_split[0]
            port = int(message_split[1])
            hexstuff = message_split[2]

            send_udp_packet(ip, port, hexstuff)

        else:
            # not the correct number of parameters
            print("ERROR: Incorrect number of parameters, 3 expected (ip, port, hex command")

    else:
        # There is no '<?>'
        print("ERROR: Syntax Error. ")
        print("There is no end of command signifier, '<?>' is needed to signify end of command")

if __name__ == '__main__':

    # Set the address and port to listen on
    comp_ip = "localhost"
    port = 52381

    # Start the listener
    p = multiprocessing.Process(target=wait_for_udp_packet, args=(comp_ip, port))
    p.start()
    p.join()


