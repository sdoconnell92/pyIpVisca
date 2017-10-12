import socket
import multiprocessing
import time
import datetime
import logging
import src.pyIPVisca as pyIPVisca


def send_udp_packet(udp_ip, udp_port, message):

    # Initialize socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    d = datetime.datetime.now()
    currentTime = str(d.second) + ":" + str(d.microsecond)
    #print("{" + currentTime + "} UDP Packet to: " + udp_ip + ":" + str(udp_port) + " |msg|: " + message)
    #logging.debug("{" + currentTime + "} UDP Packet to: " + udp_ip + ":" + str(udp_port) + " |msg|: " + message)
    try:
        print("msg0")
        print("msg1")
        sock.sendto(message.decode('hex'), (udp_ip, udp_port))
    except TypeError:
        print("ERROR: Invalid hex message.")
        print("INFO: Send Aborted")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")


if __name__ == '__main__':
    ip = '192.168.0.140'
    port = 52381
    camdir = pyIPVisca.CamMessages()

    clear_message = '01000000ffffffff'
    go_home = '010000050000003a81010604ff'
    msg = '01000005ffffffff88010001ff'
    go_preset1 = '01000007000000ff8101043F0200ff'
    GoPreset2 = '01000007000000238101043F0201ff'

    preset_header = '01000007'
    msg1 = preset_header + '00000004' + camdir.GoPreset5
    msg2 = preset_header + '00000004' + camdir.GoPreset5
    send_udp_packet(ip, port, msg1)
    time.sleep(.05)
    send_udp_packet(ip, port, msg2)