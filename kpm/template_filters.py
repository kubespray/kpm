import string
import yaml
import json
import random
import hashlib
from base64 import b64decode, b64encode


def get_hash(data, hashtype='sha1'):
    h = hashlib.new(hashtype)
    h.update(data)
    return h.hexdigest()


def rand_string(size=32, chars=(string.ascii_letters + string.digits), seed=None):
    if seed == "":
        seed = None
    random.seed(seed)
    size = int(size)
    return ''.join(random.choice(chars) for _ in range(size))


def rand_alphanum(size=32, seed=None):
    size = int(size)
    return rand_string(size=size, seed=seed)


def rand_alpha(size=32, seed=None):
    size = int(size)
    return rand_string(size=size, chars=string.ascii_letters, seed=seed)


def randint(size=32, seed=None):
    size = int(size)
    return rand_string(size=size, chars=string.digits, seed=seed)


def gen_private_ecdsa():
    from ecdsa import SigningKey
    sk = SigningKey.generate()
    return sk.to_pem()


def gen_private_rsa():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa

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
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import dsa

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


def gen_privatekey(keytype='rsa', seed=None):
    if keytype == "ecdsa":
        return gen_private_ecdsa()
    elif keytype == "rsa":
        return gen_private_rsa()
    elif keytype == "dsa":
        return gen_private_dsa()
    else:
        raise ValueError("Unknow private key type: %s" % keytype)

def jinja2(val, env):
    import jinja2
    from kpm.template_filters import jinja_filters
    from kpm.utils import convert_utf8
    jinja_env = jinja2.Environment()
    jinja_env.filters.update(jinja_filters())
    template = jinja_env.from_string(val)
    return template.render(convert_utf8(json.loads(env)))

def jsonnet(template, env):
    pass


def json_to_yaml(value):
    """
    Serializes an object as YAML. Optionally given keyword arguments
    are passed to yaml.dumps(), ensure_ascii however defaults to False.
    """
    return yaml.safe_dump(json.loads(value))


def do_json(value, **kwargs):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    import json
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(value, **kwargs)

def json_loads(value):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    import json
    return json.loads(value)

def yaml_loads(value):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    import yaml
    return yaml.load(value)


def do_yaml(value, **kwargs):
    """
    Serializes an object as YAML. Optionally given keyword arguments
    are passed to yaml.dumps(), ensure_ascii however defaults to False.
    """
    import yaml
    return yaml.dump(value,  default_flow_style=True)


def jinja_filters():
    filters = {
        'json': do_json,
        'yaml': do_yaml,
        'get_hash': get_hash,
        'b64decode': b64decode,
        'b64encode': b64encode,
        'gen_privatekey': gen_privatekey,
        'rand_alphanum': rand_alphanum,
        'rand_alpha': rand_alpha
        }
    return filters


def jsonnet_callbacks():
    filters = {
        'hash': (('data', 'hashtype'), get_hash),
        'to_yaml': (('value',), json_to_yaml),
        'rand_alphanum': (('size', 'seed'), rand_alphanum),
        'rand_alpha': (('size', 'seed'), rand_alpha),
        'randint': (('size', 'seed'), randint),
        'jinja2': (('template', 'env'), jinja2),
        'json_loads': (('jsonstr',), json_loads),
        'yaml_loads': (('jsonstr',), yaml_loads),
        'privatekey': (('keytype', "seed"), gen_privatekey),
    }
    return filters
