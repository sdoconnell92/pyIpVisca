import comunications
import ip_visca_codes as codes

ip = "192.168.0.110"
comp_ip = "192.168.0.73"
port = 52381


def send_power_off():

    comunications.send_udp_packet(ip, 52381, codes.clear_seq)
    comunications.send_udp_packet(ip, 52381, codes.power_off)

    comunications.wait_for_udp_packet(comp_ip, port)


def send_power_on():
    comunications.send_udp_packet(ip, port, codes.clear_seq)
    comunications.send_udp_packet(ip, port, codes.power_on)

    comunications.wait_for_udp_packet(comp_ip, port)


def ask_power():
    comunications.send_udp_packet(ip, port, codes.power_inq_com)

    comunications.wait_for_udp_packet(comp_ip, port)

def send_go_home():
    comunications.send_udp_packet(ip, port, codes.clear_seq)
    comunications.send_udp_packet(ip, port, codes.go_home)

    comunications.wait_for_udp_packet(comp_ip, port)

def recall_preset(preset_number):
    preset_byte = hex(preset_number)
    print preset_byte

send_power_off()