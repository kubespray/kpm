import string
import random
import hashlib
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, dsa


def get_hash(data, hashtype='sha1'):
    h = hashlib.new(hashtype)
    h.update(data)
    return h.hexdigest()


def rand_string(size=32, chars=(string.ascii_letters + string.digits)):
    size = int(size)
    return ''.join(random.choice(chars) for _ in range(size))


def rand_alphanum(size=32):
    size = int(size)
    return rand_string(size=size)


def rand_alpha(size=32):
    size = int(size)
    return rand_string(size=size, chars=string.ascii_letters)


def gen_private_ecdsa():
    from ecdsa import SigningKey
    sk = SigningKey.generate()
    return sk.to_pem()


def gen_private_rsa():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem


def gen_private_dsa():
    private_key = dsa.generate_private_key(
        key_size=1024,
        backend=default_backend()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem


def gen_privatekey(keytype='rsa'):
    if keytype == "ecdsa":
        return gen_private_ecdsa()
    elif keytype == "rsa":
        return gen_private_rsa()
    elif keytype == "dsa":
        return gen_private_dsa()
    else:
        raise ValueError("Unknow private key type: %s" % keytype)


def filters():
    filters = {
        'get_hash': get_hash,
        'b64decode': b64decode,
        'b64encode': b64encode,
        'gen_privatekey': gen_privatekey,
        'rand_alphanum': rand_alphanum,
        'rand_alpha': rand_alpha
        }
    return filters
