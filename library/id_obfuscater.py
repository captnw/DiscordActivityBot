from hashids import Hashids
from library import secretTextfile
import library.secretTextfile as secretTextfile

# Thie file obfuscates the ids of the users which are stored in the data.sqlite file for their privacy :)
# It utilizes the salt (basically a string acting as a key) from secretTextfile.py 
# which it will use to generate unique hashes, although BE WARNED, make sure you set it once and don't mess
# around with it again, unless you are aware of the risks that the hashed ids may not be decrypted properly.

HASH_MIN_LENGTH = 10
supersecret = 1234567
hashids = Hashids(salt=secretTextfile.SALT_STR, min_length=HASH_MIN_LENGTH)


def encrypt(id: int) -> str:
    ''' Obfuscates an int by changing it into a string. '''
    return hashids.encode(id)


def decrypt(hashed_id: str) -> int:
    ''' Turns the hash-string into an int '''
    return hashids.decode(hashed_id)[0]