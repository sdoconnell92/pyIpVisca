import socket
import threading
import random


class Camera:

    def __init__(self, router, camnumber, ip, port=52381):
        self.CamNumber = camnumber
        self.IP = ip
        self.Port = port
        self.ActiveMessage = None
        self.OutgoingQ = []
        self.IncomingQ = []
        self.CamRouter = router
        self.CamRouter.addcamera(self)

        print("Starting main thread for Camera " + str(self.CamNumber))
        mth = threading.Thread(target=self.main_loop)
        mth.start()

    def main_loop(self):
        while True:
            # Process any Incoming messages
            for i1 in range(0, len(self.IncomingQ)):
                msg = self.IncomingQ.pop(0)
                self.interpret_incoming(msg.Message)

            # Process any Outgoing Messages
            if self.ActiveMessage is None:
                if len(self.OutgoingQ) > 0:
                    print('Current Outgoing Q: ' + str(len(self.OutgoingQ)))
                    self.ActiveMessage = self.OutgoingQ.pop(0)
                    self.send_message()
                
    def send_message(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            print("sending message")
            sock.sendto(self.ActiveMessage.CamMessage.get_hex(),
                        (self.ActiveMessage.CamMessage.IP, self.ActiveMessage.CamMessage.Port))
            sock.close()
        except TypeError:
            print("ERROR: Invalid hex message.")
            self.ActiveMessage = None
        except socket.error:
            print("ERROR: Invalid listening address.")
            self.ActiveMessage = None
        except OverflowError:
            print("ERROR: Overflow Error. Invalid port?")
            self.ActiveMessage = None

    def interpret_incoming(self, message):
        if self.ActiveMessage is not None:
            MsgDir = CamMessages()
            if MsgDir.RpBuff1Acknowledge == message:
                self.ActiveMessage.Acknowledge = True
            if MsgDir.RpBuff1Complete == message:
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

    def add_outgoing(self, message):
        self.OutgoingQ.append(message)

    def add_incoming(self, message):
        self.IncomingQ.append(message)


class CamMessageRouter:

    def __init__(self, ip, port=52381):
        self.CamList = []
        self.IP = ip
        self.Port = port

    def start(self):
        print('Starting Camera Message Router')
        print('Initializing Camera Listen Socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.IP, self.Port))

        while True:
            data, addr = sock.recvfrom(2048)

            print('    Recieved Camera Message')
            # We have received data, lets check which camera it belongs to
            for cam in self.CamList:
                if cam.IP == str(addr[0]):
                    print('    Found Camera Message applies too')
                    # found a matching camera
                    # Create a message object
                    message = CameraMessage(CameraMessage.get_string(data))
                    # Pass the message along to the camera
                    cam.add_incoming(message)
                    break

    def addcamera(self, camera):
        try:
            self.CamList.index(camera)
        except ValueError:
            self.CamList.append(camera)


class OSCListener:

    def __init__(self, cameras, ip, port=52381):
        self.CamList = cameras
        self.IP = ip
        self.Port = port

    def start(self):

        print('Initializing OSC listen socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.IP, self.Port))

        print('Beginning OSC Listen Loop')
        while True:
            data, addr = sock.recvfrom(1024)

            # we have received an osc message
            # create a osc message object
            print('    OSC Message Recieved: ' + data)
            print('    Converting OSC Message to a Camera Message Object')
            msg = OSCMessage(OSCMessage.converttostring(data))
            msg.convertto_cammessage()

            # find the camera it is meant for
            for cam in self.CamList:
                if msg.CamMessage.IP == cam.IP:
                    print('Found Camera OSC Message is meant for')
                    cam.add_outgoing(msg)


class CameraMessage:

    def __init__(self, message=None):
        self.Message = message
        self.IP = None
        self.Port = None
        self.Acknowledge = False
        self.Complete = False
        self.Error = False

    def get_hex(self):
        return self.Message.decode('hex')

    @staticmethod
    def get_string(message):
        return message.encode('hex')

    def insert_seq(self):
        print("adding seq to: " + self.Message)
        seq = ConvertGlobalToHex()
        self.Message = self.Message.replace('00000000', seq)
        print("added seq res: " + self.Message)


class OSCMessage:

    def __init__(self, message):
        self.Message = message
        self.CamMessage = None

    @staticmethod
    def converttostring(data):
        return data.decode()

    def convertto_cammessage(self):
        result = self.convert_osc_udp(self.Message)
        self.CamMessage = CameraMessage(result[2])
        self.CamMessage.IP = result[0]
        self.CamMessage.Port = result[1]

    @staticmethod
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

                rt = [ip, port, hexstuff]
                print str(rt)
                return rt

            else:
                # not the correct number of parameters
                print("ERROR: Incorrect number of parameters, 3 expected (ip, port, hex command")

        else:
            # There is no '<?>'
            print("ERROR: Syntax Error. ")
            print("There is no end of command signifier, '<?>' is needed to signify end of command")


class CamMessages:
    def __init__(self):
        self.ClearSeq = ''
        self.GoHome = '010000050000000081010604ff'
        self.GoPreset1 = '01000007000000008101043F0200ff'
        self.GoPreset2 = '01000007000000008101043F0201ff'
        self.GoPreset3 = '01000007000000008101043F0202ff'
        self.GoPreset4 = '01000007000000008101043F0203ff'
        self.GoPreset5 = '01000007000000008101043F0204ff'
        self.GoPreset6 = '01000007000000008101043F0205ff'
        self.GoPreset7 = '01000007000000008101043F0206ff'
        self.GoPreset8 = '01000007000000008101043F0207ff'
        self.GoPreset9 = '01000007000000008101043F0208ff'
        self.GoPreset10 = '01000007000000008101043F0209ff'
        self.GoPreset11 = '01000007000000008101043F020aff'
        self.GoPreset12 = '01000007000000008101043F020bff'
        self.GoPreset13 = '01000007000000008101043F020cff'
        self.GoPreset14 = '01000007000000008101043F020dff'
        self.GoPreset15 = '01000007000000008101043F020eff'
        self.GoPreset16 = '01000007000000008101043F020fff'
        self.PowerOn = '01000006000000008101040002ff'
        self.PowerOff = '01000006000000008101040003ff'
        self.RpBuff1Acknowledge = '01110003000000009041ff'
        self.RpBuff1Complete = '01110003000000009051ff'
        self.RpBuff2Acknowledge = '01110003000000009042ff'
        self.RpBuff2Complete = '01110003000000009052ff'
        self.RpErAbnormalityInMessage = '02000002000000000f02'
        self.RpErCmdNotExecutable = '0111000400000000906241ff'
        self.RpErCmdBufferFull = '0111000400000000906003ff'

    def get_preset_list(self):
        a_list = [self.GoHome, self.GoPreset1, self.GoPreset2, self.GoPreset3, self.GoPreset4, self.GoPreset5,
                  self.GoPreset6, self.GoPreset7, self.GoPreset8, self.GoPreset9, self.GoPreset10,
                  self.GoPreset11,
                  self.GoPreset12, self.GoPreset13, self.GoPreset14, self.GoPreset15, self.GoPreset16]
        return a_list

    def get_random_preset(self):
        a_list = self.get_preset_list()
        pr_number = random.randint(0, len(a_list) - 1)
        return [pr_number, a_list[pr_number]]


def IncrementGlobal():
    global global_counter
    if global_counter[3] != 255:
        global_counter[3] += 1
    elif global_counter[2] != 255:
        global_counter[2] += 1
    elif global_counter[1] != 255:
        global_counter[1] += 1
    elif global_counter[0] != 255:
        global_counter[0] += 1

def ConvertGlobalToHex():
    global global_counter
    output = ''
    for s in global_counter:
        output += "%0.2X" % int(s)
    return output

if __name__ == '__main__':
    threadLock = threading.Lock()

    global_counter = [0, 0, 0, 0]

    print('Starting pyIPVisca')

    print('Createing Camera Message Directory')
    CamMsgDir = CamMessages()

    print('Creating Cam Message Router')
    CamRouter = CamMessageRouter('192.168.0.74')

    print('Creating Cameras')
    CamList = [Camera(CamRouter, 1, '192.168.0.110'), Camera(CamRouter, 2, '192.168.0.120'),
               Camera(CamRouter, 3, '192.168.0.130'), Camera(CamRouter, 4, '192.168.0.140'),
               Camera(CamRouter, 5, '192.168.0.150')]

    print('Creating OSC Listener')
    OSCListen = OSCListener(CamList, 'localhost')

    print('Starting OSC Listener')
    OSCpr = threading.Thread(target=OSCListen.start)
    OSCpr.start()

    print('Starting Camera Message Router')
    CRpr = threading.Thread(target=CamRouter.start)
    CRpr.start()
