class Decoder:
    def from_packets(self, packets: list):
        return ''.join([el for packet in packets for el in str(packet)])

    def from_even_bit(self):
        return

    def from_hamming(self):
        return

    def from_crc8(self):
        return

    def from_crc16(self):
        return

    def from_crc32(self):
        return