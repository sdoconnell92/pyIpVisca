import socket
import multiprocessing as mp
import time
import random
import ctypes
import logging

# go
clear_message = '01000000ffffffff'
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


def wait_for_udp_packet(udp_ip, udp_port, msg_q):

    # Set up the socket to receive
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    # Start Listening
    print("Listening on: " + udp_ip + ":" + str(udp_port))
    while True:
        # grab any messages
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        logging.debug('Received Message From Camera')
        print('Received Message: ', data)
        s = msg_q.value
        sl = s.split(',')
        sl.append(str(data))
        s = ",".join(sl)
        msg_q.value = s


if __name__ == '__main__':
    logging.basicConfig(filename="logfilepython.log", level=logging.DEBUG)
    logging.debug("Hit The Gap")
    logging.debug("v1.0.0")
    logging.debug("")

    logging.debug("Setting up shared memory")
    man = mp.Manager()
    msg_q = man.Value(ctypes.c_char_p, '')

    comp_ip = '192.168.0.74'
    comp_port = 52381
    cam_ip = '192.168.0.110'
    cam_port = 52381
    logging.debug('Computer IP: ' + comp_ip + ':' + str(cam_port))
    logging.debug('Camera IP: ' + cam_ip + ':' + str(cam_port))
    logging.debug('')
    messages = [go_home, go_preset1, go_preset2, go_preset3, go_preset4, go_preset5, go_preset6, go_preset7, go_preset8, go_preset9, go_preset10, go_preset11, go_preset12, go_preset13, go_preset14, go_preset15, go_preset16]

    logging.debug('Starting Loop...')
    for i in range(0, 40):
        logging.debug('On loop ' + str(i) + 'of 40')
        index = random.randint(0, 15)
        index2 = random.randint(0, 15)

        logging.debug('Starting Listen Process')
        p = mp.Process(target=wait_for_udp_packet, args=(comp_ip, comp_port, msg_q))
        p.start()

        logging.debug('Sending first message')
        send_udp_packet(cam_ip, cam_port, messages[index])
        while True:
            s = msg_q.value
            sl = s.split(',')
            if len(sl) >= 1:
                send_udp_packet(cam_ip, cam_port, messages[index2])
                logging.debug('Sent 2nd Message')
                p.terminate()
                break
        time.sleep(2)
