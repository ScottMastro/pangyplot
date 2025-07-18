base_to_nibble = {
    'A': 0x0,
    'C': 0x1,
    'G': 0x2,
    'T': 0x3,
    'N': 0x4,
    'END': 0xF  # use F (1111) as a terminator
}
nibble_to_base = {
    v: k for k, v in base_to_nibble.items() if k != 'END'
}

class SeqWriter:
    def __init__(self, filepath):
        self.file = open(filepath, 'wb')

    def encode_seq(self, seq):
        encoded = bytearray()
        buffer = 0
        half = False

        for base in seq:
            nibble = base_to_nibble.get(base, 0x4)  # Default to 'N'
            if not half:
                buffer = nibble << 4  # high nibble
                half = True
            else:
                buffer |= nibble  # low nibble
                encoded.append(buffer)
                half = False

        # Write END nibble
        if half:
            buffer |= base_to_nibble['END']  # as low nibble
            encoded.append(buffer)
        else:
            encoded.append(base_to_nibble['END'] << 4)  # as high nibble

        return bytes(encoded)

    def write_seq(self, seq: str):
        self.file.write(self.encode_seq(seq))

    def close(self):
        self.file.close()

class SeqReader:
    def __init__(self, filepath, offset=0):
        self.file = open(filepath, 'rb')
        self.file.seek(offset)

    def next_seq(self):
        seq = []
        while True:
            byte = self.file.read(1)
            if not byte:
                return ''.join(seq) if seq else None

            byte = byte[0]
            high = (byte >> 4) & 0xF
            low = byte & 0xF

            for nibble in [high, low]:
                if nibble == base_to_nibble['END']:
                    return ''.join(seq)
                seq.append(nibble_to_base.get(nibble, 'N'))

    def read(self, segment):
        self.file.seek(segment.offset)
        return self.next_seq()

    def read_n_seqs(self, n):
        for _ in range(n):
            seq = self.next_seq()
            if seq is None:
                break
            yield seq

    def close(self):
        self.file.close()
