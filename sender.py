import socket
from time import sleep
from encoder import Encoder
import komm
import numpy as np
from enum import Enum


class Model(Enum):
    BSC = 'BSC'


def simulate_errors(data: str, model: Model, error_probability=0.1):
    if model == Model.BSC:
        np.random.seed(1)
        bsc = komm.BinarySymmetricChannel(error_probability)
        y = bsc(list(map(int, list(data))))
        return ''.join(map(str, y))


def send_packet(packet, packet_no, model: Model, retry_no=1):
    if retry_no >= max_retries:
        print('Nie udało sie wysłać pakietu', packet)
        return

    try:

        data = f'{packet_no};{simulate_errors(packet, model)}'
        print('Sending', packet)
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
    send_packet(p, packet_no=idx, model=Model.BSC)

s.close()
