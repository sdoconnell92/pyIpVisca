import SimpleOSCtoUDPConvert as SOUC

ip = "192.168.0.140"
port = 52381
clear = '01000000ffffffff'
home = '010000050000000081010604ff'
preset0 = '01000007000000008101043f0201ff'

SOUC.send_udp_packet(ip, port, home)