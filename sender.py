import socket
from time import sleep
import encoder
import komm
import numpy as np
from enum import Enum


class Model(Enum):
    BSC = 'BSC'
    GE = 'GE'


def simulate_errors(data: str, model: Model, error_probability=0.1, prob_good_to_bad=0.1, prob_bad_to_good=0.1):
    if model == Model.BSC:
        np.random.seed(1)
        bsc = komm.BinarySymmetricChannel(error_probability)
        y = bsc([int(x) for x in list(data)])
        return ''.join(map(str, y))
    elif model == Model.GE:
        np.random.seed(1)
        ge_channel = komm.GilbertChannel(error_probability, prob_good_to_bad, prob_bad_to_good)
        y = ge_channel([int(x) for x in list(data)])
        return ''.join(map(str, y))


def send_packet(packet, packet_no, model: Model, retry_no=1):
    if retry_no >= max_retries:
        print('Nie udało sie wysłać pakietu', packet)
        return

    try:
        print('Wysyłanie', packet)
        encoded = encoder.to_even_bit(packet)
        data = f'{packet_no};{simulate_errors(encoded, model)}'
        s.send(data.encode())
        sleep(s.gettimeout())
        if s.recv(len(str(packet_no))).decode() != str(packet_no):
            send_packet(packet, packet_no=packet_no, retry_no=retry_no + 1, model=model)
    except socket.error:
        send_packet(packet, packet_no=packet_no, retry_no=retry_no + 1, model=model)


max_retries = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect(('127.0.0.1', 12345))

example_data = '10111011101110001010101110001010'
packets = encoder.to_packets(example_data, 8)
for idx, p in enumerate(packets):
    send_packet(p, packet_no=idx, model=Model.BSC)

s.close()
