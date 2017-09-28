#!/usr/bin/python2.7

import socket
import multiprocessing
import time

version = "1.03"

clear_message = '01000000ffffffff'

clear_seq =         b'\x01\x00\x00\x00\xff\xff\xff\xff'

# go
go_home =           '010000050000000081010604ff'
go_preset1 =        '01000007000000008101043F0200ff'
go_preset2 =        '01000007000000008101043F0201ff'
go_preset3 =        '01000007000000008101043F0202ff'
go_preset4 =        '01000007000000008101043F0203ff'

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


if __name__ == '__main__':

    print("PyIPVisca Unit Test")
    print("Version: " + version)
    print("Will loop through 5 different commands 40 times")
    print("")

    cam_ip = "192.168.0.110"
    cam_port = 52381
    messages = [go_home, go_preset1, go_preset2, go_preset3, go_preset4]
    sleepTimes = [4, 3, 2, 1, .5, .4, .3, .2, .1]
    sleepIndex = 0

    print("Camera IP: " + cam_ip)
    print("Camera Port: " + str(cam_port))

    for i in range(0,40):
        print("")
        print("On Loop " + str(i) + " of 40")

        for msg in messages:
            print("Sending message: " + msg)
            send_udp_packet(cam_ip, cam_port, msg)

            print("Sleeping For: " + str(sleepTimes[sleepIndex]) + "s")
            time.sleep(sleepTimes[sleepIndex])
            if sleepIndex >= len(sleepTimes) - 1:
                sleepIndex = 0
            else:
                sleepIndex += 1
