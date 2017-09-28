import socket
import random
import threading


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
                  self.GoPreset6, self.GoPreset7, self.GoPreset8, self.GoPreset9, self.GoPreset10, self.GoPreset11,
                  self.GoPreset12, self.GoPreset13, self.GoPreset14, self.GoPreset15, self.GoPreset16]
        return a_list

    def get_random_preset(self):
        a_list = self.get_preset_list()
        pr_number = random.randint(0, len(a_list) - 1)
        return [pr_number, a_list[pr_number]]


class CamMessage:

    def __init__(self, message=None):
        self.Message = message
        self.IP = None
        self.Port = None
        self.BufferIndex = -1
        self.Acknowledge = False
        self.Complete = False
        self.Error = False

    def gethex(self):
        return self.Message.decode('hex')

    @staticmethod
    def hextostring(message):
        return message.encode('hex')


class CamMessageRouter:

    def __init__(self, ip, port=52381):
        self.CamList = []
        self.IP = ip
        self.Port = port
        self.ListenOn = False

    def start(self):
        print('Starting Camera Message Router')
        self.ListenOn = True

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
                    message = CamMessage(CamMessage.hextostring(data))
                    # Pass the message along to the camera
                    cam.handleincomingmessage(message)
                    break

    def addcamera(self, camera):
        try:
            self.CamList.index(camera)
        except ValueError:
            self.CamList.append(camera)


class Camera:

    def __init__(self, router, cam_number, ip, port=52381):
        self.IP = ip
        self.Port = port
        self.CamNumber = cam_number
        self.ActiveMessageBuffer = [CamMessage(), CamMessage()]
        self.MessageQ = []
        self.ReturnMessageQ = []
        self.QEngineOn = False
        self.Router = router
        self.Router.addcamera(self)

        print("Starting main thread for Camera " + str(self.CamNumber))
        self.MainThread = threading.Thread(target=self.message_processor)
        self.MainThread.start()

    def __eq__(self, other):
        if self.IP == other.IP:
            return False

    def message_processor(self):

        while True:
            # Check the Returning Message Q
            for msg in self.ReturnMessageQ:
                self.handle_return_message(msg)

            # Check which buffers are available to take a message
            BuffersAvailable = self.checkbuffers()

            if self.checkbuffers():
                BuffIndex = 0
                # check if there is a message
                if len(self.MessageQ) > 0:
                    # add the message the the active message buffer
                    msg = self.ActiveMessageBuffer[BuffIndex] = self.MessageQ.pop(0)
                    # Send this message out
                    self.send_message(msg.CamMessage, BuffIndex)

    def checkbuffers(self):
        if self.ActiveMessageBuffer[0].Message is None:
            return True

    def oldcheckbuffers(self):
        retList = []
        if self.ActiveMessageBuffer[0].Message is None:
            retList.append(0)
        if self.ActiveMessageBuffer[1].Message is None:
            retList.append(1)
        return retList

    def handleoscmessage(self, message):
        self.MessageQ.append(message)

    def oldhandleoscmessage(self, message):
        self.send_message(message.CamMessage)

    def send_message(self, message, msg_address=-1):

        # Initialize Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            msg = message.gethex()
            sock.sendto(msg, (self.IP, self.Port))
            sock.close()
        except TypeError:
            print("ERROR: Invalid hex message.")
            print("INFO: Send Aborted")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()
        except socket.error:
            print("ERROR: Invalid listening address.")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()
        except OverflowError:
            print("ERROR: Overflow Error. Invalid port?")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()

    def oldsend_message(self, message, msg_address=-1):
        print('    Starting Send Message Process')
        if msg_address == -1:
            # the message is not in the active message q, must find a spot for it
            # Check if one of the buffers is available
            buffint = self.checkbuffers()
            if buffint == -1:
                print('    There is no buffer available for this message')
                # No buffer slot available, start the q engine to process the message q
                print('        Adding Message to q')
                self.MessageQ.append(message)
                if not self.QEngineOn:
                    print('        Starting Q Engine')
                    self.qengine()
            else:
                print('    A Buffer is available, adding message to active Q')
                message.BufferIndex = buffint
                self.ActiveMessageBuffer[message.BufferIndex] = message
        else:
            # the message is already in the active message q
            message = self.ActiveMessageBuffer[msg_address]
            message.BufferIndex = msg_address

        # Initialize socket
        print('    Initializing socket for camera message sending')
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        try:
            msg = message.gethex()
            print msg
            sock.sendto(msg, (self.IP, self.Port))
            sock.close()
        except TypeError:
            print("ERROR: Invalid hex message.")
            print("INFO: Send Aborted")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()
        except socket.error:
            print("ERROR: Invalid listening address.")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()
        except OverflowError:
            print("ERROR: Overflow Error. Invalid port?")
            self.ActiveMessageBuffer[message.BufferIndex] = CamMessages()

        if not self.Router.ListenOn:
            self.Router.start()

    def qengine(self):
        self.QEngineOn = True

        while True:
            if self.ActiveMessageBuffer[0].Message is not None:
                self.ActiveMessageBuffer[0] = self.MessageQ.pop(0)
                self.send_message(self.ActiveMessageBuffer[0], 0)
            elif self.ActiveMessageBuffer[1].Message is not None:
                self.ActiveMessageBuffer[1] = self.MessageQ.pop(0)
                self.send_message(self.ActiveMessageBuffer[1], 1)

            if len(self.MessageQ) == 0:
                break

        print('Stopping Q Engine')
        self.QEngineOn = False

    def handleincomingmessage(self, message):
        self.ReturnMessageQ.append(message)

    def handle_return_message(self, message):
        msgdirectory = CamMessages()
        if message.Message == msgdirectory.RpBuff1Acknowledge:
            self.ActiveMessageBuffer[0].Acknowledge = True
        elif message.Message == msgdirectory.RpBuff2Acknowledge:
            self.ActiveMessageBuffer[1].Acknowledge = True
        elif message.Message == msgdirectory.RpBuff1Complete:
            self.ActiveMessageBuffer[0].Complete = True
            self.ActiveMessageBuffer[0] = CamMessage()
        elif message.Message == msgdirectory.RpBuff2Complete:
            self.ActiveMessageBuffer[1].Complete = True
            self.ActiveMessageBuffer[1] = CamMessage()


class OSCMessage:

    def __init__(self, message):
        self.Message = message
        self.CamMessage = None

    @staticmethod
    def converttostring(data):
        return data.decode()

    def convertto_cammessage(self):
        result = self.convert_osc_udp(self.Message)
        self.CamMessage = CamMessage(result[2])
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
                    cam.handleoscmessage(msg)

if __name__ == '__main__':
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
