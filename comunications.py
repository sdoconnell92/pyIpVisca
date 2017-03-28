import socket
import ip_visca_codes as codes
import multiprocessing as mp
import time


def send_udp_packet(udp_ip, udp_port, message):

    print("UDP target IP:", udp_ip)
    print("UDP target port:", udp_port)
    print("message:", message)

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (udp_ip, udp_port))


def wait_for_udp_packet(udp_ip, udp_port, queue_item=mp.Queue):

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_ip, udp_port))

    import time
    millis = int(round(time.time() * 1000))
    print(millis)
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        millis = int(round(time.time() * 1000))
        print("received message:|(" + str(millis) + ")| ", data )
        queue_item.put(data)


def send_visca_command(ip, port, visca_hex, expected_completion_time=10, acknowlege_msg="", compl_msg=""):

    # Set up a listener in another process to grab udp responses
    q1 = mp.Queue
    p1 = mp.Process(target=wait_for_udp_packet, args=(ip, port, q1))
    p1.start()

    command_reset_recieved = False
    visca_acknowledge_recieved = False
    completion_recieved = False

    send_udp_packet(ip, port, visca_hex)
    time.sleep(1)
    messages = q1.get()
    for message in iter(q1.get, None):  # Replace `None` as you need
        # Check if the message is a recognized
        if message == acknowlege_msg:
            visca_acknowledge_recieved = True
        elif message == compl_msg:
            completion_recieved = True

    # Check if we have been acknowleged


