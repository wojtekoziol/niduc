import socket
from time import sleep
from encoder import Encoder


def send_packet(packet, packet_no, retry_no=1):
    if retry_no >= max_retries:
        print('Nie udało sie wysłać pakietu', packet)
        return

    try:
        data = f'{packet_no};{packet}'
        print('Sending', data)
        s.send(data.encode())
        sleep(s.gettimeout())
        if s.recv(len(str(packet_no))).decode() != str(packet_no):
            send_packet(packet, packet_no=packet_no, retry_no=retry_no + 1)
    except socket.error:
        send_packet(packet, packet_no=packet_no, retry_no=retry_no + 1)


max_retries = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect(('127.0.0.1', 12345))

example_data = '10111011101110001010101110001010'
encoder = Encoder()
packets = encoder.to_packets(example_data, 8)
for idx, p in enumerate(packets):
    send_packet(p, packet_no=idx)

s.close()
