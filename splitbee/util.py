import string
import random


# The default alphabet is all letters and digits, but with some confusing
# duplicate-looking letters removed (see below for the whole list).
ID_TRANSLATION = ''.join([chr(x) for x in range(256)])
DEFAULT_ALPHABET = (string.ascii_letters + string.digits).translate(
    ID_TRANSLATION,
    'oO0Il1'
)
def gen_random(length, alphabet=DEFAULT_ALPHABET):
    return ''.join(random.choice(alphabet) for x in range(length))
