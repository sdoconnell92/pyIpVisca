import socket

# go
go_home =           '010000050000000081010604ff'
go_preset1 =        '01000007000000008101043F0200ff'
go_preset2 =        '01000007000000008101043F0201ff'
go_preset3 =        '01000007000000008101043F0202ff'
go_preset4 =        '01000007000000008101043F0203ff'
go_preset5 =        '01000007000000008101043F0204ff'
go_preset6 =        '01000007000000008101043F0205ff'
go_preset7 =        '01000007000000008101043F0206ff'
go_preset8 =        '01000007000000008101043F0207ff'
go_preset9 =        '01000007000000008101043F0208ff'
go_preset10 =        '01000007000000008101043F0209ff'
go_preset11 =        '01000007000000008101043F020aff'
go_preset12 =        '01000007000000008101043F020bff'
go_preset13 =        '01000007000000008101043F020cff'
go_preset14 =        '01000007000000008101043F020dff'
go_preset15 =        '01000007000000008101043F020eff'
go_preset16 =        '01000007000000008101043F020fff'
clear_message = '01000000ffffffff'


def send_udp_packet(udp_ip, udp_port, message):
    # Initialize socket
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP

    #sock.sendto(clear_message.decode('hex'), (udp_ip, udp_port))
    print("Sending UDP Packet to: " + udp_ip + ":" + str(udp_port) + " |msg|: " + message)
    try:
        sock.sendto(message.decode('hex'), (udp_ip, udp_port))
    except TypeError:
        print("ERROR: Invalid hex message.")
        print("INFO: Send Aborted")
    except socket.error:
        print("ERROR: Invalid listening address.")
    except OverflowError:
        print("ERROR: Overflow Error. Invalid port?")


if __name__ == '__main__':
    send_udp_packet('192.168.0.120', 52381, go_home)
