from SimpleOSCtoUDPConvert import wait_for_udp_packet
import socket

try:
    wait_for_udp_packet("192.168.10.22", -231)
except OverflowError:
    print"sadjfo"
