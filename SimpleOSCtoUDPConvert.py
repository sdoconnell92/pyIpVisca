#!/usr/bin/python2.7

import socket
import multiprocessing
import time


class OscCommandListener:

    def __init__(self, osc_ip, osc_port):
        self.OscIP = osc_ip
        self.OscPort = osc_port

        # Set up the socket to receive
        self.sock = socket.socket(socket.AF_INET,  # Internet
                            socket.SOCK_DGRAM)  # UDP
        self.sock.bind((self.OscIP, self.OscPort))

        # Set up the process to listen
        q = multiprocessing.Queue
        self.ListenProcess = multiprocessing.Process(target=self.wait_for_udp_packet())
        self.ListenProcess.start()

    def wait_for_udp_packet(self):

        # Start Listening
        converted_message = None
        print("Listening for OSC on: " + self.OscIP + ":" + str(self.OscPort))
        while True:
            # grab any messages
            data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes

            # Try to convert the osc packet to udp
            # If it doesn't succeed due to unicode decode error
            #      This means that it is a message from the camera since it is in hex code
            print("")
            print("Received OSC Message: ", data)
            print("Sending to converter...")
            try:
                converted_message = self.convert_osc_udp(data.decode())
            except UnicodeDecodeError:
                pass
                print("Received Cam Message: ", data)

            # Set up a camera connection
            conn = CameraConnection(converted_message[0], int(converted_message[1]))

            # Send the message to the camera
            conn.send_command(converted_message[2])

    def convert_osc_udp(self, message=""):
        # message format: "192.168.0.0::52381::hex-message<?>"

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

                ReturnArray = [ip, port, hexstuff]
                return ReturnArray

            else:
                # not the correct number of parameters
                print("ERROR: Incorrect number of parameters, 3 expected (ip, port, hex command")

        else:
            # There is no '<?>'
            print("ERROR: Syntax Error. ")
            print("There is no end of command signifier, '<?>' is needed to signify end of command")


class CameraConnection:

    def __init__(self, cam_ip, cam_port):
        self.CamIP = cam_ip
        self.CamPort = cam_port
        self.ComputerIP = None

        # Initialize the socket connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((cam_ip, 52381))
        self.ComputerIP = self.sock.getsockname()[0]
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Initialize listening connection
        self.ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_command(self, cam_command):

        # Create process for listening to the camera
        q = multiprocessing.Queue()
        listen_process = multiprocessing.Process(target=self.listen_to_camera, args=(q,))
        listen_process.start()

        # Get a list of the messages to expect from the camera
        codes = IpViscaCodes()
        expected_messages = codes.get_message_class(cam_command)

        ack_received = False
        comp_received = False
        sending_index = 1

        while not ack_received:
            # Send the command
            self.sock.sendto(cam_command.decode('hex'), (self.CamIP, self.CamPort))

            # Wait for the Camera timeout
            time.sleep(0.1)

            # Check if we have received an acknowledgement message
            returned_messages = q.get()
            for message in returned_messages:
                if expected_messages.check_message(message.data) == "Acknowledgement":
                    ack_recieved = True
                elif expected_messages.check_message(message.data) == "Completion":
                    comp_received = True

            if ack_received:
                print("Camera Acknowledged Command: " + cam_command)
                if comp_received:
                    print("Camera Completed Command: " + cam_command)
            else:
                print("Camera Acknowledgement Timeout Reached")
                print("Resending Command: " + cam_command)

            if sending_index > 1:
                print("ERROR: Could not communicate with the camera")
                print("Aborting camera connection")

            sending_index += 1

        starting_ms = int(round(time.time() * 1000))
        while not comp_received:
            returned_messages = q.get()

            for message in returned_messages:
                if expected_messages.check_message(message.data) == "Completion":
                    comp_received = True

            if comp_received:
                print("Camera has completed command: " + cam_command)
            else:
                # Check if we have reached timeout for this message
                current_ms = int(round(time.time() * 1000))
                ms_difference = current_ms - starting_ms
                if ms_difference >= expected_messages.Timeout:
                    print("Camera has not returned a completion message")
                    print("We are assuming that it has completed")

    def listen_to_camera(self, q1):
        sock = self.sock
        messages_from_cam = []

        if self.ComputerIP is not None:
            print("Computer Ip: " + self.ComputerIP)
            print("Cam Port: " + str(self.CamPort))
            self.ListenSocket.bind((self.ComputerIP, int(self.CamPort)))

        # Start listening
            while True:
                # grab any messages
                data, addr = self.ListenSocket.recvfrom(1024)

                # need to check if this message is from our camera
                if True:
                    print("Received Camera Message ( " + str(addr) + "): " + str(data))
                    msg = CameraMessagesData()
                    msg.data = data
                    msg.addr = addr
                    messages_from_cam.append(msg)

                    # put the message list in the queue
                    q1.put(messages_from_cam)


# Create a class for transferring data from camera listening thread to the send command thread
class CameraMessagesData:

    def __init__(self):
        self.data = None
        self.addr = None


class ExpectedCameraReturn:

    def __init__(self, cam_command, reset_message, acknowledgement, completion, timeout):
        self.CamCommand = cam_command
        self.ResetMessage = None
        self.Acknowledgement = None
        self.Completion = None
        self.Timeout = 10 * 1000

    def check_message(self, cam_message):

        if cam_message == self.ResetMessage:
            return 'Reset Message'
        elif cam_message == self.Acknowledgement:
            return 'Acknowledgement'
        elif cam_message == self.Completion:
            return 'Completion'
        else:
            return None


# ---------------------------------------------------------------------------------
# IP Visca Codes
# ---------------------------------------------------------------------------------
class IpViscaCodes:

    def __init__(self):
        # Utility
        clear_seq = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x00\xff\xff\xff\xff',
                                         reset_message='\x00',
                                         acknowledgement='\x00',
                                         completion='\x00',
                                         timeout=0.2)
        self.ClearSeq = clear_seq
        power_on = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x06\x00\x00\x00\x00\x81\x01\x04\x00\x02\xff',
                                        reset_message='\x00',
                                        acknowledgement='\x00',
                                        completion='\x00',
                                        timeout=1)
        self.PowerOn = power_on
        power_off = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x06\x00\x00\x00\x00\x81\x01\x04\x00\x03\xff',
                                         reset_message='\x00',
                                         acknowledgement='\x00',
                                         completion='\x00',
                                         timeout=1)

        self.PowerOff = power_off

        # Go Commands
        go_home = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x05\x00\x00\x00\x00\x81\x01\x06\x04\xff',
                                       reset_message='\x02\x01\x00\x01\xff\xff\xff\xff\x01',
                                       acknowledgement='\x01\x11\x00\x03\x00\x00\x00\x00\x90\x41\xff',
                                       completion='\x01\x11\x00\x03\x00\x00\x00\x00\x90\x51\xff',
                                       timeout=1)
        self.GoHome = go_home
        go_preset_0 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x00\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=1)
        self.GoPreset0 = go_preset_0
        go_preset_1 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x01\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset1 = go_preset_1
        go_preset_2 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x02\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset2 = go_preset_2
        go_preset_3 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x03\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset3 = go_preset_3
        go_preset_4 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x04\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset4 = go_preset_4
        go_preset_5 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x05\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset5 = go_preset_5
        go_preset_6 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x06\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset6 = go_preset_6
        go_preset_7 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x07\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset7 = go_preset_7
        go_preset_8 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x08\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset8 = go_preset_8
        go_preset_9 = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x09\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPreset9 = go_preset_9
        go_preset_a = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0a\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetA = go_preset_a
        go_preset_b = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0b\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetB = go_preset_b
        go_preset_c = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0c\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetC = go_preset_c
        go_preset_d = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x0d\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetD = go_preset_d
        go_preset_e = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x0e\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetE = go_preset_e
        go_preset_f = ExpectedCameraReturn(cam_command=b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x0f\xff',
                                           reset_message='\x00',
                                           acknowledgement='\x00',
                                           completion='\x00',
                                           timeout=7)
        self.GoPresetF = go_preset_f

    def get_message_class(self, camera_command):
        cam_command = camera_command.decode('hex')
        print("cam_command: " + cam_command)
        if cam_command == self.ClearSeq.CamCommand:
            return self.ClearSeq
        elif cam_command == self.PowerOn.CamCommand:
            return self.PowerOn
        elif cam_command == self.PowerOff.CamCommand:
            return self.PowerOff
        elif cam_command == self.GoPreset0.CamCommand:
            return self.GoPreset0
        elif cam_command == self.GoPreset1.CamCommand:
            return self.GoPreset1
        elif cam_command == self.GoPreset2.CamCommand:
            return self.GoPreset2
        elif cam_command == self.GoPreset3.CamCommand:
            return self.GoPreset3
        elif cam_command == self.GoPreset4.CamCommand:
            return self.GoPreset4
        elif cam_command == self.GoPreset5.CamCommand:
            return self.GoPreset5
        elif cam_command == self.GoPreset6.CamCommand:
            return self.GoPreset6
        elif cam_command == self.GoPreset7.CamCommand:
            return self.GoPreset7
        elif cam_command == self.GoPreset8.CamCommand:
            return self.GoPreset8
        elif cam_command == self.GoPreset9.CamCommand:
            return self.GoPreset9
        elif cam_command == self.GoPresetA.CamCommand:
            return self.GoPresetA
        elif cam_command == self.GoPresetB.CamCommand:
            return self.GoPresetB
        elif cam_command == self.GoPresetC.CamCommand:
            return self.GoPresetC
        elif cam_command == self.GoPresetD.CamCommand:
            return self.GoPresetD
        elif cam_command == self.GoPresetE.CamCommand:
            return self.GoPresetE
        elif cam_command == self.GoPresetF.CamCommand:
            return self.GoPresetF


if __name__ == '__main__':

    # Set the address and port to listen on
    OscIp = "localhost"
    OscPort = 52381

    # Create OscCommandListener class
    listener = OscCommandListener(osc_ip=OscIp, osc_port=OscPort)
