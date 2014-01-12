from itertools import imap
import string

from more_itertools import chunked


class Bytes(object):
    """
    A sequence of 8-bit bytes.
    """

    def __init__(self, bytes):
        self._bytes = ''.join(bytes)

    def __repr__(self):
        return self._bytes

    def __eq__(self, other):
        return self._bytes == other._bytes

    def __neq__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return iter(self._bytes)

    def __len__(self):
        return len(self._bytes)

    def chunked(self, n):
        """
        Return generator of substring chunks.
        """
        return imap(self.__class__, chunked(self._bytes, n))

    def to_base64(self):
        alphabet = _get_base64_alphabet()
        bits = self.to_binary()

        chars = []
        for _6bits in bits.chunked(6):
            index = _6bits.to_integer()
            chars.append(alphabet[index])

        return Base64EncodedBytes(chars)

    def to_binary(self):
        """
        Return binary representation of bytes.

        Return value is string of '0' and '1' characters.
        """
        return BinaryEncodedBytes(
            Integer(ord(b)).to_binary()
            for b in self._bytes
        )

    def to_hex(self):
        return HexEncodedBytes(
            hex(ord(b))[2:] for b in self._bytes
        )


class BinaryEncodedBytes(Bytes):
    """
    A sequence of '0' and '1' bytes representing raw binary data.
    """
    def to_bytes(self):
        return Bytes(
            chr(bits.to_integer())
            for bits in self.chunked(8)
        )

    def to_integer(self):
        return int(self._bytes, 2)


class HexEncodedBytes(Bytes):
    """
    A sequence of ASCII characters in [0-9a-f] (2 chars per byte).
    """
    def to_bytes(self):
        return Bytes(
            chr(int(b._bytes, 16))
            for b in self.chunked(2)
        )


class Base64EncodedBytes(Bytes):
    """
    A sequence of ASCII characters in [0-9a-zA-Z+/] (4 chars per 3 bytes).
    """
    def to_bytes(self):
        alphabet = _get_base64_alphabet()
        bits = []
        for b in self._bytes:
            i = Integer(alphabet.index(b))
            _6bits = i.to_binary()[2:]
            bits.extend(_6bits)
        return BinaryEncodedBytes(bits).to_bytes()


def _get_base64_alphabet():
    lower = string.letters[:26]
    upper = string.letters[26:]
    numerals = ''.join(map(bytes, range(0, 10)))
    return upper + lower + numerals + '+/'


class Integer(object):
    def __init__(self, i):
        self._i = i

    def to_binary(self):
        return self._pad8(bin(self._i)[2:])

    @staticmethod
    def _pad8(s):
        """
        Left pad with zeros to width 8.
        """
        return '%08d' % int(s)
