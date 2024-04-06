class Encoder:
    def to_packets(self, data: str, packet_size: int):
        return [int(data[i:i+packet_size]) for i in range(0, len(data), packet_size)]

    def to_even_bit(self):
        return

    def to_hamming(self):
        return

    def to_crc8(self):
        return

    def to_crc16(self):
        return

    def to_crc32(self):
        return