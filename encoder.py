import zlib
import crcmod

class Encoder:
    def to_packets(self, data: str, packet_size: int):
        return [int(data[i:i+packet_size]) for i in range(0, len(data), packet_size)]

    def to_even_bit(data):
        count = data.count("1")
        if count % 2 == 0:
            parity_bit = "0"
        else:
            parity_bit = "1"
        return data + parity_bit

    def to_crc8(binary_sequence):
        crc8 = crcmod.predefined.Crc('crc-8')
        crc8.update(binary_sequence.encode())
        crc_value = crc8.crcValue
        encoded_sequence = binary_sequence + format(crc_value, '08b')
        return encoded_sequence

    def to_crc16(data):
        crc16 = crcmod.predefined.Crc('crc-16')
        crc16.update(data.encode())
        crc_value = crc16.crcValue
        encoded_sequence = data + format(crc_value, '016b')
        return encoded_sequence

    def to_crc32(data):
        crc32 = zlib.crc32(data.encode())
        return data + format(crc32 & 0xFFFFFFFF, '032b')
