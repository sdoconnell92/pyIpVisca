import socket
import threading
import random
import logging
import re
import time


class Camera:
    def __init__(self, router, osc_listener, cam_number, ip, port=52381):
        self.CamNumber = cam_number
        self.IP = ip
        self.Port = port
        self.ActiveMessage = None
        self.OutgoingQ = []
        self.IncomingQ = []
        self.OutgoingEvent = threading.Event()
        self.IncomingEvent = threading.Event()
        self.CamRouter = router
        self.CamRouter.add_camera(self)
        self.OSCListener = osc_listener
        self.OSCListener.add_camera(self)
        self.Logger = logging.getLogger(__name__)

        try:
            self.Logger.info('Starting Incoming Processor for Camera ' + str(self.CamNumber))
            thread_name = 'Camera ' + str(self.CamNumber) + 'IncPrc'
            inc_thr = threading.Thread(name=thread_name, target=self.incoming_processor)
            inc_thr.start()
        except RuntimeError:
            self.Logger.exception('Could not start Camera %d Incoming Processor' % self.CamNumber)

        try:
            self.Logger.info('Starting Outgoing Processor for Camera ' + str(self.CamNumber))
            thread_name = 'Camera ' + str(self.CamNumber) + 'OutPrc'
            out_thr = threading.Thread(name=thread_name, target=self.outgoing_processor)
            out_thr.start()
        except RuntimeError:
            self.Logger.exception('Could not start Camera %d Outgoing Processor' % self.CamNumber)

    def incoming_processor(self):
        while True:
            if len(self.IncomingQ) == 0:
                self.Logger.debug('Waiting for Incoming Message Event on Camera ' + str(self.CamNumber))
                self.IncomingEvent.wait()
            else:
                # Process any Incoming messages
                for i1 in range(0, len(self.IncomingQ)):
                    msg = self.IncomingQ.pop(0)
                    logging.debug('Handling message from Camera '
                                  + str(self.CamNumber) + ": "
                                  + msg.message)
                    self.interpret_incoming(msg)
                
    def outgoing_processor(self):
        while True:
            # Process any Outgoing Messages
            if self.ActiveMessage is None:
                if len(self.OutgoingQ) == 0:
                    self.Logger.debug('Waiting for Outgoing Message Event on Camera ' + str(self.CamNumber))
                    self.OutgoingEvent.wait()
                else:
                    self.Logger.info('Camera %d Q: %d' % (self.CamNumber, len(self.OutgoingQ)))
                    self.ActiveMessage = self.OutgoingQ.pop(0)
                    self.send_message()

    def send_message(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Get the next available sequence number
            seq = seq_counter.increment()
            # Insert sequence into the message
            self.ActiveMessage.CamMessage.insert_seq(seq)
            seq_string = self.ActiveMessage.CamMessage.get_seq_string()

            self.Logger.info('Sending Message to Camera %d: %s' %
                             (self.CamNumber, self.ActiveMessage.CamMessage.message))

            sock.sendto(self.ActiveMessage.CamMessage.get_hex(),
                        (self.ActiveMessage.CamMessage.IP, self.ActiveMessage.CamMessage.Port))

            self.ActiveMessage.CamMessage.set_sent_time()
            msg_timeout = threading.Timer(5, self.message_timeout_handler, [seq_string])
            msg_timeout.start()

            sock.close()
        except TypeError:
            self.Logger.exception("ERROR: |%s| Invalid hex message." %
                                  self.ActiveMessage.CamMessage.get_seq_string())
            self.ActiveMessage = None
        except socket.error:
            self.Logger.exception("ERROR: |%s| Invalid listening address." %
                                  self.ActiveMessage.CamMessage.get_seq_string())
            self.ActiveMessage = None
        except OverflowError:
            self.Logger.exception("ERROR: |%s| Overflow Error. Invalid port?" %
                                  self.ActiveMessage.CamMessage.get_seq_string())
            self.ActiveMessage = None
        except OSError:
            self.Logger.exception('OSError while sending message For Camera %d' %
                                  self.CamNumber)

    def interpret_incoming(self, message):
        if self.ActiveMessage is not None:
            msg_dir = CamMessages()

            if msg_dir.RpBuff1Acknowledge == message.get_payload():
                self.Logger.info('Message(%s) For IP(%s) Acknowledged' % (message.get_seq_string(), message.IP))
                self.ActiveMessage.Acknowledge = True

            elif msg_dir.RpBuff1Complete == message.get_payload():
                self.Logger.info('Message(%s) For IP(%s) Completed' % (message.get_seq_string(), message.IP))
                d = time.time() - self.ActiveMessage.CamMessage.SentTime
                logging.getLogger(msg_comp_time).info('Message(%s) Completed In %d' %
                                                      (message.get_seq_string(), d))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpBuff2Acknowledge == message.get_payload():
                self.Logger.info('Message(%s) For IP(%s) Acknowledged' % (message.get_seq_string(), message.IP))
                self.ActiveMessage.Acknowledge = True

            elif msg_dir.RpBuff2Complete == message.get_payload():
                self.Logger.info('Message(%s) For IP(%s) Completed' % (message.get_seq_string(), message.IP))
                d = time.time() - self.ActiveMessage.CamMessage.SentTime
                logging.getLogger(msg_comp_time).info('Message(%s) Completed In %d' %
                                                      (message.get_seq_string(), d))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpInqComplete == message.get_payload():
                self.Logger.info('Inquiry(%s) For IP(%s) Completed' % (message.get_seq_string(), message.IP))
                d = time.time() - self.ActiveMessage.CamMessage.SentTime
                logging.getLogger(msg_comp_time).info('Message(%s) Completed In %d' %
                                                      (message.get_seq_string(), d))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpCmdCancelComplete == message.get_payload():
                self.Logger.info('Command Cancel(%s) For IP(%s) Completed' % (message.get_seq_string(), message.IP))
                d = time.time() - self.ActiveMessage.CamMessage.SentTime
                logging.getLogger(msg_comp_time).info('Message(%s) Completed In %d' %
                                                      (message.get_seq_string(), d))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpCmdCancelNoSocket == message.get_payload():
                self.Logger.error('Command Cancel(%s) For IP(%s) No Socket' % (message.get_seq_string(), message.IP))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpIFClearComplete == message.get_payload():
                self.Logger.info('IF Clear(%s) For IP(%s) Completed' % (message.get_seq_string(), message.IP))
                d = time.time() - self.ActiveMessage.CamMessage.SentTime
                logging.getLogger(msg_comp_time).info('Message(%s) Completed In %d' %
                                                      (message.get_seq_string(), d))
                self.ActiveMessage.Complete = True
                self.ActiveMessage = None

            elif msg_dir.RpErAbnormalityInSequence == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Abnormality In Sequence' %
                                  (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            elif msg_dir.RpErAbnormalityInMessage == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Abnormality In Message' %
                                  (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            elif msg_dir.RpErBuff1CmdNotExecutable == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Buffer 1 Command Not Executable' %
                                  (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            elif msg_dir.RpErBuff2CmdNotExecutable == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Buffer 2 Command Not Executable' %
                                  (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            elif msg_dir.RpErCmdBufferFull == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Command Buffer Full' % (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            elif msg_dir.RpErSyntaxError == message.get_payload():
                self.Logger.error('Message(%s) For IP(%s) Syntax Error' % (message.get_seq_string(), message.IP))
                self.ActiveMessage = None

            else:
                self.Logger.error('Unrecognized Response From Camera %d' % self.CamNumber)

    def message_timeout_handler(self, seq_number):
        self.Logger.debug('Message timeout handler started on Camera %d, seq %s' %
                          (self.CamNumber, seq_number))
        if self.ActiveMessage is not None:
            if self.ActiveMessage.CamMessage.get_seq_string() == seq_number:
                self.Logger.debug('Setting Active Message to None on Camera %d due to timeout' % self.CamNumber)
                self.ActiveMessage = None

    def add_outgoing(self, message):
        self.Logger.debug('Adding Outgoing Message(%s) to Camera %d' %
                          (message.CamMessage.get_seq_string(), self.CamNumber))
        self.OutgoingQ.append(message)
        self.OutgoingEvent.set()
        self.OutgoingEvent.clear()

    def add_incoming(self, message):
        self.Logger.debug('Adding Incoming Message(%s) to Camera %d' %
                          (message.get_seq_string(), self.CamNumber))
        self.IncomingQ.append(message)
        self.IncomingEvent.set()
        self.IncomingEvent.clear()


class CamMessageRouter:
    def __init__(self, ip, port=52381):
        self.CamList = []
        self.IP = ip
        self.Port = port
        self.Logger = logging.getLogger(__name__)

    def start(self):
        self.Logger.debug('Initializing Camera Router Socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind((self.IP, self.Port))
        except socket.error:
            self.Logger.exception('Error encountered when trying to bind router socket to computer ip')

        while True:
            self.Logger.debug("Camera router waiting for message")
            data, addr = sock.recvfrom(1024)
            # We have received data

            # Create a message object
            message = CameraMessage(CameraMessage.get_string(data), str(addr[0]))
            self.Logger.debug("Camera Message(%s) Received: %s" %
                              (message.get_seq_string(), message.message))

            # Lets check which camera it belongs to
            for cam in self.CamList:
                self.Logger.debug("Comparing Camera %d IP(%s) to incoming message(%s) IP(%s)" %
                                  (cam.CamNumber, cam.IP, message.get_seq_string(), str(addr[0])))
                if cam.IP == str(addr[0]):
                    # found a matching camera
                    # Pass the message along to the camera
                    cam.add_incoming(message)
                    break

    def add_camera(self, camera):
        try:
            self.Logger.debug('Checking if Camera %d is present in Camera Message Router CamList' % camera.CamNumber)
            self.CamList.index(camera)
        except ValueError:
            self.Logger.debug("Adding Camera %d to Camera Message Router" % camera.CamNumber)
            self.CamList.append(camera)


class OSCListener:
    def __init__(self, ip, port=52381):
        self.CamList = []
        self.IP = ip
        self.Port = port
        self.Logger = logging.getLogger(__name__)

    def start(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind((self.IP, self.Port))
        except socket.error:
            self.Logger.exception('Error encountered when trying to bind listener socket to localhost')

        while True:
            self.Logger.debug('Initializing OSC Listener Socket')
            data, addr = sock.recvfrom(1024)

            self.Logger.debug('Raw OSC Message (%s): %s' % (addr, data))

            # we have received an osc message
            # create a osc message object
            msg = OSCMessage(OSCMessage.convert_to_string(data))
            msg.convert_to_cam_message()

            self.Logger.info("OSC Message Received: %s" % msg.CamMessage.message)

            # find the camera it is meant for
            for cam in self.CamList:
                self.Logger.debug("Comparing Camera %d IP(%s) to outgoing OSC message(%s) IP(%s)" %
                                  (cam.CamNumber, cam.IP, msg.CamMessage.get_seq_string(), msg.CamMessage.IP))
                if msg.CamMessage.IP == cam.IP:
                    self.Logger.debug("Adding message(%s) to Camera %d Outgoing Q" %
                                      (msg.CamMessage.get_seq_string(), cam.CamNumber))
                    cam.add_outgoing(msg)
                    
    def add_camera(self, camera):
        try:
            self.Logger.debug('Checking if Camera %d is present in OSC Message Listener CamList' % camera.CamNumber)
            self.CamList.index(camera)
        except ValueError:
            self.Logger.debug("Adding Camera %d to OSC Message Listener" % camera.CamNumber)
            self.CamList.append(camera)


class CameraMessage:
    def __init__(self, cam_msg=None, cam_ip=None):
        self.MessageDeconstructed = self.deconstruct(cam_msg)
        self.IP = cam_ip
        self.Port = None
        self.Acknowledge = False
        self.Complete = False
        self.Error = False
        self.Logger = logging.getLogger(__name__)
        self.SentTime = None

    @property
    def message(self):
        self.Logger.debug('Returning camera message in string format')
        l = []
        for i in self.MessageDeconstructed:
            l.append(str(i))
        return ''.join(l)
    
    @property
    def sequence(self):
        self.Logger.debug('Returning camera message sequence number in list format')
        return self.MessageDeconstructed[4:8]

    def get_hex(self):
        self.Logger.debug('Returning camera message hex format')
        return self.message.decode('hex')

    @staticmethod
    def get_string(message):
        return message.encode('hex')

    @staticmethod
    def deconstruct(message):
        return re.findall(r'.{1,2}', message, re.DOTALL)

    def get_seq_string(self):
        self.Logger.debug('Returning camera message sequence number in string format')
        l = []
        for i in self.sequence:
            l.append(str(i))
        return ''.join(l)

    def insert_seq(self, sequence):
        self.Logger.debug('Inserting new sequence number into Camera Message')
        if len(self.MessageDeconstructed) != 0:
            self.MessageDeconstructed[4:8] = sequence

    def get_header(self):
        self.Logger.debug('Returning camera message header in string format')
        return ''.join(self.MessageDeconstructed[:8])

    def get_payload(self):
        self.Logger.debug('Returning camera message payload in string format')
        return ''.join(self.MessageDeconstructed[8:])

    def get_payload_type(self):
        self.Logger.debug('Returning camera message payload type in string format')
        return ''.join(self.MessageDeconstructed[:2])

    def get_payload_length(self):
        self.Logger.debug('Returning camera message payload length in string format')
        return ''.join(self.MessageDeconstructed[2:4])

    def set_sent_time(self):
        self.SentTime = time.time()


class OSCMessage:
    def __init__(self, message):
        self.Message = message
        self.CamMessage = None
        self.Logger = logging.getLogger(__name__)

    @staticmethod
    def convert_to_string(data):
        return data.decode()

    def convert_to_cam_message(self):
        self.Logger.debug('Converting OSC Message to Camera Message')
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
                return rt

            else:
                # not the correct number of parameters
                logging.error("ERROR: Incorrect number of parameters, 3 expected (ip, port, hex command")

        else:
            # There is no '<?>'
            logging.error("ERROR: Syntax Error. ")
            logging.error("There is no end of command signifier, '<?>' is needed to signify end of command")


class CamMessages:
    def __init__(self):
        self.ClearSeq = ''
        self.IFClear = '81010001ff'
        self.GoHome = '81010604ff'
        self.GoPreset1 = '8101043F0200ff'
        self.GoPreset2 = '8101043F0201ff'
        self.GoPreset3 = '8101043F0202ff'
        self.GoPreset4 = '8101043F0203ff'
        self.GoPreset5 = '8101043F0204ff'
        self.GoPreset6 = '8101043F0205ff'
        self.GoPreset7 = '8101043F0206ff'
        self.GoPreset8 = '8101043F0207ff'
        self.GoPreset9 = '8101043F0208ff'
        self.GoPreset10 = '8101043F0209ff'
        self.GoPreset11 = '8101043F020aff'
        self.GoPreset12 = '8101043F020bff'
        self.GoPreset13 = '8101043F020cff'
        self.GoPreset14 = '8101043F020dff'
        self.GoPreset15 = '8101043F020eff'
        self.GoPreset16 = '8101043F020fff'
        self.PowerOn = '8101040002ff'
        self.PowerOff = '8101040003ff'

        self.RpBuff1Acknowledge = '9041ff'
        self.RpBuff1Complete = '9051ff'
        self.RpBuff2Acknowledge = '9042ff'
        self.RpBuff2Complete = '9052ff'
        self.RpInqComplete = '905002ff'
        self.RpCmdCancelComplete = '906204ff'
        self.RpCmdCancelNoSocket = '906205ff'
        self.RpIFClearComplete = '9050ff'

        self.RpErAbnormalityInSequence = '0f01'
        self.RpErAbnormalityInMessage = '0f02'
        self.RpErBuff1CmdNotExecutable = '906141ff'
        self.RpErBuff2CmdNotExecutable = '906241ff'
        self.RpErCmdBufferFull = '906003ff'
        self.RpErSyntaxError = '906002ff'

        # self.PowerOn = '01000006000000008101040002ff'
        # self.PowerOff = '01000006000000008101040003ff'
        # self.RpBuff1Acknowledge = '01110003000000009041ff'
        # self.RpBuff1Complete = '01110003000000009051ff'
        # self.RpBuff2Acknowledge = '01110003000000009042ff'
        # self.RpBuff2Complete = '01110003000000009052ff'
        # self.RpErAbnormalityInMessage = '02000002000000000f02'
        # self.RpErCmdNotExecutable = '0111000400000000906241ff'
        # self.RpErCmdBufferFull = '0111000400000000906003ff'
        self.Logger = logging.getLogger(__name__)

    def get_preset_list(self):
        self.Logger.debug('Returning List of preset commands')
        a_list = [self.GoHome, self.GoPreset1, self.GoPreset2, self.GoPreset3, self.GoPreset4, self.GoPreset5,
                  self.GoPreset6, self.GoPreset7, self.GoPreset8, self.GoPreset9, self.GoPreset10,
                  self.GoPreset11,
                  self.GoPreset12, self.GoPreset13, self.GoPreset14, self.GoPreset15, self.GoPreset16]
        return a_list

    def get_random_preset(self):
        self.Logger.debug('Returning a random preset command')
        a_list = self.get_preset_list()
        pr_number = random.randint(0, len(a_list) - 1)
        return [pr_number, a_list[pr_number]]


class SequenceCounter:

    def __init__(self):
        self.seq = [0, 0, 0, 0]
        self.lock = threading.Lock()
        self.Logger = logging.getLogger(__name__)

    def increment(self):
        old_seq = self.to_hex()
        self.lock.acquire()
        if self.seq[3] != 255:
            self.seq[3] += 1
        elif self.seq[2] != 255:
            self.seq[2] += 1
        elif self.seq[1] != 255:
            self.seq[1] += 1
        elif self.seq[0] != 255:
            self.seq[0] += 1
        else:
            self.seq = [0, 0, 0, 0]
        self.lock.release()
        self.Logger.debug('Incrementing sequence: Old=%s, New=%s' % (old_seq, self.to_hex()))
        return self.to_hex_list()

    def to_hex(self):
        self.Logger.debug('Converting sequence list to hex string')
        output = ''
        for s in self.seq:
            output += str("%0.2X" % int(s))
        return output

    def to_hex_list(self):
        self.Logger.debug('Converting sequence list to hex list')
        output = []
        for i in self.seq:
            output.append(str("%0.2X" % int(i)))
        return output


def safe_print(message):
    print(message + "\n")


if __name__ == '__main__':
    # Start logging module
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)-10s - %(levelname)-8s - %(message)s')

    fh = logging.FileHandler('pyIPVisca.log')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)

    msg_comp_time = 'msg_comp_time'
    logging.getLogger(msg_comp_time).propagate = False
    fhc = logging.FileHandler('Msg_Completion_Time.log')
    logging.getLogger(msg_comp_time).addHandler(fhc)

    # Create a sequence Counter Object
    seq_counter = SequenceCounter()

    logging.info('Starting pyIPVisca')

    # Create Camera Message Directory
    CamMsgDir = CamMessages()

    # Create the Camera Message Router
    CamRouter = CamMessageRouter('192.168.0.74')

    # Create the OSC Listener
    OSCListen = OSCListener('localhost')

    # Create the Cameras
    CamList = [Camera(CamRouter, OSCListen, 1, '192.168.0.110'), Camera(CamRouter, OSCListen, 2, '192.168.0.120'),
               Camera(CamRouter, OSCListen, 3, '192.168.0.130'), Camera(CamRouter, OSCListen, 4, '192.168.0.140'),
               Camera(CamRouter, OSCListen, 5, '192.168.0.150')]

    # Start the OSC Listener
    logging.info('Starting OSC Listener')
    OSCpr = threading.Thread(target=OSCListen.start)
    OSCpr.start()

    # Start the Camera Router
    logging.info('Starting Camera Message Router')
    CRpr = threading.Thread(target=CamRouter.start)
    CRpr.start()
