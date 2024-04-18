import socket
from time import sleep
import decoder

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 12345))
s.listen(5)

c, addr = s.accept()
packets = []

data = '0'
while data != '':
    data = c.recv(1024).decode()
    if data == '' or ';' not in data:
        continue
    packet_no, packet = data.split(';')[0:2]
    print('Otrzymano', packet_no, packet)
    decoded = decoder.to_even_bit_decode(packet)
    if int(packet_no) >= len(packets) and decoded is not None:
        packets.append(decoded)
        sleep(2)
        c.send(packet_no.encode())

print('Otrzymane dane', decoder.from_packets(packets))
c.close()
