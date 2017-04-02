#!/usr/bin/python2.7

import socket
import multiprocessing
import time

# ---------------------------------------------------------------------------------
# IP Visca Codes
# ---------------------------------------------------------------------------------
clear_seq = b'\x01\x00\x00\x00\xff\xff\xff\xff'

# go
power_on = b'\x01\x00\x00\x06\x00\x00\x00\x00\x81\x01\x04\x00\x02\xff'
power_off = b'\x01\x00\x00\x06\x00\x00\x00\x00\x81\x01\x04\x00\x03\xff'
go_home = b'\x01\x00\x00\x05\x00\x00\x00\x00\x81\x01\x06\x04\xff'
go_preset_0 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x00\xff'
go_preset_1 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x01\xff'
go_preset_2 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x02\xff'
go_preset_3 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3F\x02\x03\xff'
go_preset_4 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x04\xff'
go_preset_5 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x05\xff'
go_preset_6 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x06\xff'
go_preset_7 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x07\xff'
go_preset_8 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x08\xff'
go_preset_9 = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x09\xff'
go_preset_a = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0a\xff'
go_preset_b  = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0b\xff'
go_preset_c = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0c\xff'
go_preset_d = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0d\xff'
go_preset_e = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0e\xff'
go_preset_f = b'\x01\x00\x00\x07\x00\x00\x00\x00\x81\x01\x04\x3f\x02\x0f\xff'


class OscCommandListener():

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


class CameraConnection():

    def __init__(self, cam_ip, cam_port):
        self.CamIP = cam_ip
        self.CamPort = cam_port
        self.ComputerIP = None

        # Initialize the socket connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((cam_ip, 52381))
        self.ComputerIP = self.sock.getsockname()[0]

    def send_command(self, cam_command):

        # Create process for listening to the camera
        q = multiprocessing.Queue
        listen_process = multiprocessing.Process(target=self.listen_to_camera, args=q)
        listen_process.start()

        # Get a list of the messages to expect from the camera
        expected_messages = ExpectedCameraReturn(cam_command)

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
            sock.bind(self.ComputerIP, self.CamPort)

        # Start listening
            while True:
                # grab any messages
                data, addr = sock.recvfrom(1024)

                # need to check if this message is from our camera
                if True:
                    print("Received Camera Message ( " + addr + "): " + data)
                    msg = CameraMessagesData
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

    def __init__(self, cam_command):
        self.ResetMessage = None
        self.Acknowledgement = None
        self.Completion = None
        self.Timeout = 10 * 1000

        # Fill out the message variables based on the cam_command

    def check_message(self, cam_message):

        if cam_message == self.ResetMessage:
            return 'Reset Message'
        elif cam_message == self.Acknowledgement:
            return 'Acknowledgement'
        elif cam_message == self.Completion:
            return 'Completion'
        else:
            return None



if __name__ == '__main__':

    # Set the address and port to listen on
    comp_ip = "localhost"
    port = 52381
    cam_net_comp_ip = "0.0.0.0"

    # Start the listener
    p = multiprocessing.Process(target=wait_for_udp_packet, args=(comp_ip, port))
    p.start()


