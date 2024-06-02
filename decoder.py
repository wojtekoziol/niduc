import crcmod
import zlib


def from_packets(packets: list):
    return ''.join([el for packet in packets for el in str(packet)])


def to_even_bit_decode(binary_sequence):
    count_ones = binary_sequence.count('1')
    if count_ones % 2 == 0:
        return binary_sequence[:-1]
    else:
        return None


def to_crc8_decode(encoded_sequence):
    crc8 = crcmod.predefined.Crc('crc-8')
    data = encoded_sequence[:-8]
    received_crc = int(encoded_sequence[-8:], 2)
    crc8.update(data.encode())
    calculated_crc = crc8.crcValue
    if calculated_crc == received_crc:
        return data
    else:
        return None


def to_crc16_decode(encoded_sequence):
    crc16 = crcmod.predefined.Crc('crc-16')
    data = encoded_sequence[:-16]
    received_crc = int(encoded_sequence[-16:], 2)
    crc16.update(data.encode())
    calculated_crc = crc16.crcValue
    if calculated_crc == received_crc:
        return data
    else:
        return None


def to_crc32_decode(encoded_sequence):
    encoded_length = len(encoded_sequence)
    crc_length = 32
    data_length = encoded_length - crc_length
    data = encoded_sequence[:data_length]
    received_crc = int(encoded_sequence[data_length:], 2)
    calculated_crc = zlib.crc32(data.encode()) & 0xFFFFFFFF
    if calculated_crc == received_crc:
        return data
    else:
        return None
