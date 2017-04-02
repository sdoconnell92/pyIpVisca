import socket

def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('192.168.43.1', 52381))
    return s.getsockname()[0]

print my_ip()