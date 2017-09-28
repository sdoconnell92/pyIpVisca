#!/usr/bin/python2.7

import socket
import multiprocessing
import time
import random

version = "1.03"

clear_message = '01000000ffffffff'

clear_seq =         b'\x01\x00\x00\x00\xff\xff\xff\xff'

# go
go_home =           '010000050000000081010604ff'
go_preset1 =        '01000007000000008101043F0200ff'
go_preset2 =        '01000007000000008101043F0201ff'
go_preset3 =        '01000007000000008101043F0202ff'
go_preset4 =        '01000007000000008101043F0203ff'
go_preset5 =        '01000007000000008101043F0204ff'
go_preset6 =        '01000007000000008101043F0205ff'
go_preset7 =        '01000007000000008101043F0206ff'
go_preset8 =        '01000007000000008101043F0207ff'
go_preset9 =        '01000007000000008101043F0208ff'
go_preset10 =        '01000007000000008101043F0209ff'
go_preset11 =        '01000007000000008101043F020aff'
go_preset12 =        '01000007000000008101043F020bff'
go_preset13 =        '01000007000000008101043F020cff'
go_preset14 =        '01000007000000008101043F020dff'
go_preset15 =        '01000007000000008101043F020eff'
go_preset16 =        '01000007000000008101043F020fff'



def send_udp_packet(udp_ip, udp_port, message):

    # Initialize socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    print("Sending Clear Message to: " + udp_ip + ":" + str(udp_port) + "|msg|: " + clear_message)
    try:
        #sock.sendto(clear_message.decode('hex'), (udp_ip, udp_port))
        did = 94
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


if __name__ == '__main__':

    print("PyIPVisca Unit Test")
    print("Version: " + version)
    print("Will loop through 5 different commands 40 times")
    print("")

    cam_ips = ["192.168.0.110", "192.168.0.120", "192.168.0.130", "192.168.0.140", "192.168.0.150"]
    cam_port = 52381
    messages = [go_home, go_preset1, go_preset2, go_preset3, go_preset4, go_preset5, go_preset6, go_preset7, go_preset8, go_preset9, go_preset10, go_preset11, go_preset12, go_preset13, go_preset14, go_preset15, go_preset16]

    send_udp_packet(cam_ips[1], cam_port, go_preset3)