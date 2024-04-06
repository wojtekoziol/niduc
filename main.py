import komm

from encoder import Encoder
from decoder import Decoder


data = "10111011101110001010101110001010"
encoder = Encoder()
packets = encoder.to_packets(data, 4)
print(packets)
decoder = Decoder()
print(decoder.from_packets(packets))

