from sys import implementation as _implementation
if _implementation.name != 'circuitpython':
    raise NotImplementedError("Woah there, Bud! You can only do IR stuff from CircuitPython!")

import pulseio
import board
import digitalio
import adafruit_irremote
from .timeout import Timeout

#irPin = digitalio.DigitalInOut(board.A0)
#irPin.direction = digitalio.Direction.INPUT
DEFAULT_PULSEIN = pulseio.PulseIn(board.A0, maxlen=30000, idle_state=True)
DEFAULT_DECODER = adafruit_irremote.GenericDecode()

def decode_chunk(decoder, pulsein) -> bytes:
    pulses = decoder.read_pulses(pulsein)
    try:
        buf = bytes(decoder.decode_bits(pulses))
        print(".", end="")
        return buf
    except adafruit_irremote.IRNECRepeatException:
        return b''
    except adafruit_irremote.IRDecodeException:
        return b''
    except adafruit_irremote.FailedToDecode:
        return b''

def decode_line(decoder, pulsein) -> bytes:
    buf = b''
    for i in range(10):
        buf += decode_chunk(decoder, pulsein)
        if buf.endswith(b'\r\n'):
            break
    return buf

class IRMsg:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body
    
    @property
    def division(self):
        return self.headers[b'Division'].decode()

    @property
    def text(self):
        return self.body.decode()

def receive(timeout: int = 10, line_timeout: int = 100, decoder = DEFAULT_DECODER, pulsein = DEFAULT_PULSEIN) -> IRMsg:

    @Timeout(timeout)
    def wait_for_bell():
        # Read until BELL
        print("*", end="")
        while decode_chunk(decoder, pulsein) != b'\x07':
            pass
        return True

    if not wait_for_bell():
        return None

    t_wd = Timeout(line_timeout)
    @t_wd
    def receive_the_thing():
        buf = b'\x07'
        # Read until no BELL
        print("*", end="")
        while buf == b'\x07' or buf == b'':
            buf = decode_chunk(decoder, pulsein)
            t_wd.reset()
        # Figure out datagram length
        print("*", end="")
        total_length = int.from_bytes(buf, 'big')
        read_length = 0
        if total_length < 8:
            return None
        # Start receiving the datagram
        print("*", end="")
        protocol = decode_line(decoder, pulsein)
        t_wd.reset()
        read_length += len(protocol)
        if protocol != b"CSMSG/1.0\r\n":
            print("Potentially unsupported protocol version. Try getting the latest servercom library?")
        headers = {}
        buf = b': '
        while buf.find(b': ') >= 0 or buf == b'\r\n':
            print("*", end="")
            buf = decode_line(decoder, pulsein)
            t_wd.reset()
            read_length += len(buf)
            if buf == b'\r\n':
                break
            split_buf = buf.strip(b'\r\n').split(b': ')
            headers.update({split_buf[0]: split_buf[1]})
        body = b''
        content_length = int(headers[b'Content-Length'])
        while len(body) < content_length:
            print("*", end="")
            body += decode_chunk(decoder, pulsein)
            t_wd.reset()
        return IRMsg(headers, body)
    return receive_the_thing()

#dude = receive()
#print()
#print(dude.division)
#print(dude.text)
