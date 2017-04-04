import SimpleOSCtoUDPConvert as SOUC

ip = "192.168.0.140"
port = 52381
message = '010000050000000081010604ff'

SOUC.send_udp_packet(ip, port, message)