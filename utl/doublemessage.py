import socket
import time
import datetime
import random


def send_udp_packet(udp_ip, udp_port, message):
    d = datetime.datetime.now()
    currentTime = str(d.second) + ":" + str(d.microsecond)
    print("{" + currentTime + "} UDP Packet to: " + udp_ip + ":" + str(udp_port) + " |msg|: " + message)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.decode('hex'), (udp_ip, udp_port))
    except TypeError:
        print("ERROR: Invalid hex message.")
        print("INFO: Send Aborted")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")


# Function for receiving all udp packets on specified network: for us localhost
def wait_for_udp_packet(udp_ip, udp_port):

    # Set up the socket to receive
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((udp_ip, udp_port))

        # Start Listening
        print("Listening on: " + udp_ip + ":" + str(udp_port))
        while True:
            # grab any messages
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes


class CamMessages:

    def __init__(self):
        self.Header = '01000007'
        # self.GoPreset1 = '8101043F0200ff'
        # self.GoPreset2 = '8101043F0201ff'
        # self.GoPreset3 = '8101043F0202ff'
        # self.GoPreset4 = '8101043F0203ff'
        # self.GoPreset5 = '8101043F0204ff'
        # self.GoPreset6 = '8101043F0205ff'
        # self.GoPreset7 = '8101043F0206ff'
        # self.GoPreset8 = '8101043F0207ff'
        # self.GoPreset9 = '8101043F0208ff'
        # self.GoPreset10 = '8101043F0209ff'
        # self.GoPreset11 = '8101043F020aff'
        # self.GoPreset12 = '8101043F020bff'
        # self.GoPreset13 = '8101043F020cff'
        # self.GoPreset14 = '8101043F020dff'
        # self.GoPreset15 = '8101043F020eff'
        # self.GoPreset16 = '8101043F020fff'
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

    def get_preset_list(self):
        a_list = [self.GoPreset1, self.GoPreset2, self.GoPreset3, self.GoPreset4, self.GoPreset5,
                  self.GoPreset6, self.GoPreset7, self.GoPreset8, self.GoPreset9, self.GoPreset10, self.GoPreset11,
                  self.GoPreset12, self.GoPreset13, self.GoPreset14, self.GoPreset15, self.GoPreset16]
        return a_list

    def get_random_preset(self):
        a_list = self.get_preset_list()
        pr_number = random.randint(0, len(a_list) - 1)
        return [pr_number, a_list[pr_number]]

    def get_preset(self, index):
        global global_counter
        IncrementGlobal()
        seq = ConvertGlobalToHex()
        pr = self.get_preset_list()[index]
        return self.Header + seq + pr


class Camera:

    def __init__(self, cam_number, ip, port=52381):
        self.IP = ip
        self.Port = port
        self.CamNumber = cam_number

    def send_message(self, message):
        # Initialize socket
        # message format: "192.168.0.0::52381::hexmessage<?>"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = self.IP + "::" + str(self.Port) + "::" + message + "<?>"
        try:
            sock.sendto(msg, ('localhost', self.Port))
            sock.close()
        except TypeError:
            print("ERROR: Invalid hex message.")
            print("INFO: Send Aborted")
        except socket.error:
            print("ERROR: Invalid listening address.")
        except OverflowError:
            print("ERROR: Overflow Error. Invalid port?")


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
    global_counter = [0, 0, 0, 0]
    print("Starting Program")
    print("Grabbing Preset List")
    presets = CamMessages()
    print("Creating Cameras")
    cam_list = [Camera(1, '192.168.0.110'), Camera(2, '192.168.0.120'), Camera(3, '192.168.0.130'),
                Camera(6, '192.168.0.140'), Camera(5, '192.168.0.150')]

    pr = presets.get_random_preset()
    cam_list[0].send_message(pr[1])

    print("Starting While Loop")
    i1 = 0
    # while True:
    #     print("While Loop: " + str(i1))
    #     print("Looping through cameras")
    #     for cam in cam_list:
    #         print("     On Camera: " + str(cam.CamNumber))
    #         pr = presets.get_random_preset()
    #         pr2 = presets.get_random_preset()
    #         not_same = False
    #         while not not_same:
    #             pr2 = presets.get_random_preset()
    #             if pr[0] == pr2[0]:
    #                 not_same = False
    #             else:
    #                 not_same = True
    #         print("          Sending Preset: " + str(pr[0]) + '|||' + str(pr[1]))
    #         cam.send_message(pr[1])
    #         #time.sleep(.2)
    #         print("          Sending Preset: " + str(pr2[0]) + '|||' + str(pr2[1]))
    #         cam.send_message(pr2[1])
    #
    #     time.sleep(2)
    #     i1 += 1
