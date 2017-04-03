import socket

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
print("Listening On: 192.168.0.73:52381")
sock.bind(("192.168.0.73", 52381))
while True:
    data, addr = sock.recvfrom(1024)
    print(data.encode('hex'))

