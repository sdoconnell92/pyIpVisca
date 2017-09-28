import threading
import Queue
import socket
import datetime
import time

clear_message = '01000000ffffffff'


class OSCListener:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        pass

    def run(self):
        global OSCQ
        # Set up the socket to receive
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((self.ip, self.port))

        # Start Listening
        while True:
            # grab any messages
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            OSCQ.put(data)


class Camera:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ready = True
        self.buff1ready = True
        self.buff2ready = True
        self.messages = []
        self.cam_messages = []

    def send_message(self, message):
        # Initialize socket
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

        d = datetime.datetime.now()
        currentTime = str(d.second) + ":" + str(d.microsecond)
        print("{" + currentTime + "} UDP Packet to: " + self.ip + ":" + str(self.port) + " |msg|: " + message)
        try:
            sock.sendto(message.decode('hex'), (self.ip, self.port))
        except TypeError:
            print("ERROR: Invalid hex message.")
            print("INFO: Send Aborted")
        except socket.error:
            print("ERROR: Invalid listening address.")
        except OverflowError:
            print("ERROR: Overflow Error. Invalid port?")

    def wait_for_ready(self):
        print('starting wait for ready')
        while True:
            if self.buff1ready:
                if len(self.messages) > 0:
                    self.buff1ready = False
                    msg = self.messages[0]
                    self.messages.remove(msg)
                    self.send_message(msg)
            elif self.buff2ready:
                if len(self.messages) > 0:
                    self.buff2ready = False
                    msg = self.messages[0]
                    self.messages.remove(msg)
                    self.send_message(msg)

    def handle_cam_messages(self):
        print('starting handle cam messages')
        while True:
            if len(self.cam_messages) > 0:
                print("cam_message found in queue")
                msg = self.cam_messages[0]
                self.cam_messages.remove(msg)
                datastr = msg.encode('hex')
                if datastr.find('9042ff') > -1 or datastr.find('9041ff') > -1:
                    print("found buff 1 complete")
                    # buffer 1 has completed
                    self.buff1ready = True
                elif datastr.find('9052ff') > -1 or datastr.find('9051ff') > -1:
                    print("found buff 2 complete")
                    # buffer 2 has completed
                    self.buff2ready = True

    def add_message(self, message):
        self.messages.append(message)

    def add_cam_message(self, message):
        self.cam_messages.append(message)


class CamCommunicator:

    def __init__(self):
        self.messages = []
        self.cameras = []
        self.cameras = [Camera('192.168.0.110', 52381), Camera('192.168.0.120', 52381), Camera('192.168.0.130', 52381), Camera('192.168.0.140', 52381), Camera('192.168.0.150', 52381)]
        for Cam in self.cameras:
            p = threading.Thread(target=Cam.wait_for_ready, args=())
            p.start()
            c = threading.Thread(target=Cam.handle_cam_messages, args=())
            c.start()

    def run(self):
        global OSCQ
        while True:
            if not OSCQ.empty():
                somedata = OSCQ.get()
                print(somedata)
                datadict = convert_osc_udp(somedata)
                for i1 in range(0, len(self.cameras) - 1):
                    if self.cameras[i1].ip == datadict['ip']:
                        self.cameras[i1].add_message(datadict['message'])

    def wait_for_cam_msg(self):
        # Set up the socket to receive
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind(('192.168.0.74', 52381))

        # Start Listening
        print("Listening on: ")
        while True:
            # grab any messages
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print('cam message recieved: ' + data.encode('hex'))
            u = threading.Thread(target=self.give_msg_to_cam, args=(addr, data))
            u.start()

    def give_msg_to_cam(self, addr, data):
        for Cam in self.cameras:
            if str(addr).find(Cam.ip) > -1:
                print('matching cam found')
                Cam.add_cam_message(data)


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

            returndict = {}
            returndict['ip'] = ip
            returndict['port'] = port
            returndict['message'] = hexstuff

            return returndict

        else:
            # not the correct number of parameters
            print("ERROR: Incorrect number of parameters, 3 expected (ip, port, hex command")

    else:
        # There is no '<?>'
        print("ERROR: Syntax Error. ")
        print("There is no end of command signifier, '<?>' is needed to signify end of command")


if __name__ == '__main__':
    print('Starting Program...')
    OSCQ = Queue.Queue()

    OSCListen = OSCListener('localhost', 52381)
    CamCom = CamCommunicator()

    print('Starting OSC Listenner...')
    OSCThread = threading.Thread(target=OSCListen.run, args=())
    OSCThread.start()

    print('i am')
    CamThread = threading.Thread(target=CamCom.run, args=())
    CamThread.start()

    CamListen = threading.Thread(target=CamCom.wait_for_cam_msg, args=())
    CamListen.start()
