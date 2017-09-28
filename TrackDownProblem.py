import mido
import multiprocessing as mp
import socket
import time
import logging
LOG_FILENAME = 'example.log'
logging.basicConfig(filename="logingfile",level=logging.DEBUG)

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
        print("Received Cam Message From [" + str(addr) + "]: ", data)
        logging.debug("Received Cam Message From [" + str(addr) + "]: " + str(data))

if __name__ == "__main__":

    comp_ip = "192.168.0.74"
    comp_port = 52381

    p = mp.Process(target=wait_for_udp_packet, args=(comp_ip, comp_port))
    p.start()

    SmallKeyboard = mido.open_output('IAC Driver Small')
    LargeKeyboard = mido.open_output('IAC Driver Large')

    for SmallIndex in range(24, 48):

        Smallon = mido.Message('note_on', note=SmallIndex)
        Smalloff = mido.Message('note_off', note=SmallIndex)

        print('Sending SmallKey: ' + str(Smallon))
        SmallKeyboard.send(Smallon)
        time.sleep(.5)
        print('Sending SmallKey: ' + str(Smalloff))
        logging.debug('Sending SmallKey: ' + str(Smalloff))
        SmallKeyboard.send(Smalloff)

        for LargeIndex in range(0, 86):
            msg = mido.Message('note_on', note=LargeIndex)
            print('Sending Large: ' + str(msg))
            logging.debug('Sending Large: ' + str(msg))
            LargeKeyboard.send(msg)

            time.sleep(.5)
            msg = mido.Message('note_off', note=LargeIndex)
            print('Sending Large: ' + str(msg))
            LargeKeyboard.send(msg)

            time.sleep(3)

