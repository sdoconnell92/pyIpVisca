import socket
import multiprocessing


recieved_message = []

def wait_for_udp_packet(udp_ip, udp_port):

    print("Listening on: " + udp_ip + ":" + str(udp_port))
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
        #recieved_message.append(data)
        try:
            convert_osc_udp(data.decode())
        except UnicodeDecodeError:
            pass

 
def send_udp_packet(udp_ip, udp_port, message):

    print("UDP target IP:", udp_ip)
    print("UDP target port:", udp_port)
    print("message:", message)

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(bytes.fromhex(message), (udp_ip, udp_port))

def convert_osc_udp(message=""):
    # message format: "192.168.0.0::52381::hexmessage<?>"
    x1 = message.find("<?>")
    if x1 != 0:
        message = message[:x1]

        message_split = message.split('::')
        if len(message_split) == 3:
            ip = message_split[0]
            port = int(message_split[1])
            hexstuff = message_split[2]

            send_udp_packet(ip, port, hexstuff)

if __name__ == '__main__':
    comp_ip = "192.168.0.73"
    cam_ip = "192.168.0.110"
    port = 52381

    p = multiprocessing.Process(target=wait_for_udp_packet, args=(comp_ip, port))
    p.start()
    p.join()
