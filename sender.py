import socket
from time import sleep
import Encoder
import numpy as np
from enum import Enum
import random
import komm


class Model(Enum):
    BSC = 'BSC'
    GE = 'GE'


class GilbertElliott:
    def __init__(self, p_good_to_bad, p_bad_to_good, p_error_bad):
        self.p_good_to_bad = p_good_to_bad
        self.p_bad_to_good = p_bad_to_good
        self.p_error_bad = p_error_bad
        self.state = 'G'

    def transmit(self, bit):
        if self.state == 'G':
            if np.random.rand() < self.p_good_to_bad:
                self.state = 'B'
        else:
            if np.random.rand() < self.p_bad_to_good:
                self.state = 'G'

        if self.state == 'B' and np.random.rand() < self.p_error_bad:
            return '1' if bit == '0' else '0'
        return bit


def simulate_errors(data: str, model: Model, error_probability=0.001, prob_good_to_bad=0.1, prob_bad_to_good=0.1):
    if model == Model.BSC:
        np.random.seed(1)
        bsc = komm.BinarySymmetricChannel(error_probability)
        y = bsc([int(x) for x in list(data)])
        return ''.join(map(str, y))
    elif model == Model.GE:
        np.random.seed(1)
        ge = GilbertElliott(prob_good_to_bad, prob_bad_to_good, error_probability)
        y = [ge.transmit(bit) for bit in data]
        return ''.join(y)


def send_packet(packet, packet_no, model: Model, error_probability, choice, retry_no=1):
    if retry_no > max_retries:
        return False
    try:
        if choice == 0:
            encoded = Encoder.to_even_bit(packet)
        elif choice == 1:
            encoded = Encoder.to_crc8(packet)
        elif choice == 2:
            encoded = Encoder.to_crc16(packet)
        elif choice == 3:
            encoded = Encoder.to_crc32(packet)
        data = f'{packet_no};{simulate_errors(encoded, model, error_probability)}'
        s.send(data.encode())
        sleep(s.gettimeout())
        response = s.recv(1024).decode()
        if ';' in response:
            response_packet_no, received_packet = response.split(';', 1)
            if response_packet_no == str(packet_no):
                return True
        return send_packet(packet, packet_no, model, error_probability, choice, retry_no + 1)
    except socket.error:
        return send_packet(packet, packet_no, model, error_probability, choice, retry_no + 1)


def generate_random_binary_sequence(length):
    return ''.join(random.choice(['0', '1']) for _ in range(length))


def calculate_ber(sent_data, received_data):
    errors = sum(1 for sent, received in zip(sent_data, received_data) if sent != received)
    total_bits = len(sent_data)
    if total_bits == 0:
        return 0
    return errors / total_bits


def calculate_group_errors(sent_data, received_data, group_size):
    group_errors = 0
    for i in range(0, len(sent_data), group_size):
        if sent_data[i:i + group_size] != received_data[i:i + group_size]:
            group_errors += 1
    return group_errors

def transmission_with_arq(packets, model, error_probability, choice):
    received_data = []
    error_count = 0
    total_retries = 0

    for idx, p in enumerate(packets):
        retries = 0
        while not send_packet(p, packet_no=idx, model=model, error_probability=error_probability, choice=choice,
                              retry_no=retries):
            retries += 1
            total_retries += 1
            if retries > max_retries:
                error_count += 1
                break
        if error_count > max_error_frames:
            print("Przekroczono maksymalną liczbę błędnych ramek.")
            break
        try:
            response = s.recv(1024).decode()
            if ';' in response:
                packet_no, received_packet = response.split(';', 1)
                received_data.append(received_packet)
        except socket.timeout:
            error_count += 1
            if error_count > max_error_frames:
                print("Przekroczono maksymalną liczbę błędnych ramek.")
                break

    # Obliczenie BER oraz błędów grupowych
    received_data_flat = ''.join(received_data[:len(example_data)])
    independent_error_count = sum(1 for sent, received in zip(example_data, received_data_flat) if sent != received)
    return received_data_flat, error_count, total_retries, independent_error_count

def transmission_without_arq(packets, model, error_probability, choice):
    received_data = []

    for idx, p in enumerate(packets):
        if choice == 0:
            encoded = Encoder.to_even_bit(p)
        elif choice == 1:
            encoded = Encoder.to_crc8(p)
        elif choice == 2:
            encoded = Encoder.to_crc16(p)
        elif choice == 3:
            encoded = Encoder.to_crc32(p)
        data = simulate_errors(encoded, model, error_probability)
        received_data.append(data)

    # Obliczenie BER oraz błędów grupowych
    received_data_flat = ''.join(received_data[:len(example_data)])
    independent_error_count = sum(1 for sent, received in zip(example_data, received_data_flat) if sent != received)
    return received_data_flat, independent_error_count


# Ustawienia
max_retries = 0
max_error_frames = 20  #parametr maksymalnej liczby błędnych ramek
error_probability = 0.0001  # Przykładowe prawdopodobieństwo błędu
model = Model.GE  # Wybór modelu kanału
prob_good_to_bad = 0.1  # Prawdopodobieństwo przejścia ze stanu dobrego do złego (dla GE)
prob_bad_to_good = 0.1  # Prawdopodobieństwo przejścia ze stanu złego do dobrego (dla GE)
choice = 1  # 0-Bit parzystosci, 1-crc8, 2-crc16, 3-crc32
sequence_length = 2048
group_size = 4

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.1)
try:
    s.connect(('127.0.0.1', 12345))
except socket.timeout:
    print("Timeout: Could not connect to the server.")
    s.close()
    exit()

random_binary_sequence = generate_random_binary_sequence(sequence_length)
example_data = random_binary_sequence
packets = Encoder.to_packets(example_data, 32)

# Transmisja z ARQ
received_data_arq, error_count_arq, total_retries, independent_errors_arq = transmission_with_arq(packets, model, error_probability, choice)
ber_arq = calculate_ber(example_data, received_data_arq)
group_errors_arq = calculate_group_errors(example_data, received_data_arq, group_size)

# Transmisja bez ARQ
received_data_no_arq, independent_errors_no_arq = transmission_without_arq(packets, model, error_probability, choice)
ber_no_arq = calculate_ber(example_data, received_data_no_arq)
group_errors_no_arq = calculate_group_errors(example_data, received_data_no_arq, group_size)

# Zamknij gniazdo
s.close()

# Wyniki
print("Transmisja z ARQ:")
print(f"Bit Error Rate (BER): {ber_arq}")
print(f"Liczba błędów grupowych: {group_errors_arq}")
print(f"Liczba błędów niezależnych: {independent_errors_arq}")

print("\nTransmisja bez ARQ:")
print(f"Bit Error Rate (BER): {ber_no_arq}")
print(f"Liczba błędów grupowych: {group_errors_no_arq}")
print(f"Liczba błędów niezależnych: {independent_errors_no_arq}")
