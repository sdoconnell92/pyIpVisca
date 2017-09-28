import socket
import multiprocessing


class ClassCommunicator:

    def __init__(self):
        self.mgr = multiprocessing.Manager()
        self.namespace = self.mgr.Namespace()
        self.event = multiprocessing.Event()


class CameraMessage:

    def  __init__(self, data, addr):
        self.address = addr
        self.message = data


class CameraListener:

    def __init__(self, ComManager, ip_param, port_param):
        self.ip = ip_param
        self.port = port_param
        self.ComManager = ComManager

        # Set up the socket to receive
        self.sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.sock.bind((self.ip, self.port))

    def start_listening(self):
        pass

    def listen_loop(self):
        while True:
            # grab any messages
            data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes

            CamMsg = CameraMessage(data, addr)
            a_list = []
            a_list = self.ComManager.namespace.value
            a_list.append(CamMsg)
            self.ComManager.namespace.value = a_list


class OSCListener:

    def __init__(self, ComManager):
        pass

    def start_listening(self):
        pass

    def route_message(self, cam_instances = []):
        pass

    def listen_loop(self):
        pass


class CameraCommunicator:

    def __init__(self):
        self.OSCMessageQueue = []
        self.MessageQueue = []
        self.Buffer1Acknowledge = True
        self.Buffer1Completion = True
        self.Buffer2Acknowledge = True
        self.Buffer2Completion = True
        self.ip = '192.168.0.110'
        self.port = 52381
        pass

    def start_loop(self):
        pass

    def send_message(self, message):
        pass

    def convert_osc(self, message):
        pass

    def listen_loop(self):
        pass


if __name__ == '__main__':
    ComputerIP = '192.168.0.74'
    ComPort = 52381

    Cam1 = CameraCommunicator()
    Cam2 = CameraCommunicator()
    Cam3 = CameraCommunicator()
    Cam4 = CameraCommunicator()
    Cam5 = CameraCommunicator()
    CamList = [Cam1, Cam2, Cam3, Cam4, Cam5]

    CamComIn = ClassCommunicator()
    OSCComIn = ClassCommunicator()

    CamMessageListener = CameraListener(CamComIn, ComputerIP, ComPort)

    while True:

        CamMessages = []
        CamMessages = CamComIn.ns.value
        for i1 in range(0, len(CamMessages) - 1):
            msg = CamMessages[i1]
            for i2 in range(0, len(CamList) - 1):
                cam = CamList[i2]
                if msg.address == cam.ip:
                    cam.MessageQueue.append(msg)