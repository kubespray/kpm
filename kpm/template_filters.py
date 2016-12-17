import jinja2
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
    return rand_string(size=int(size), seed=seed)


def rand_alpha(size=32, seed=None):
    return rand_string(size=int(size), chars=string.ascii_letters, seed=seed)


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


all_privates = {}


def gen_privatekey(keytype='rsa', key='', seed=None):
    if seed is None:
        seed = rand_alphanum(128)
    k = seed + key
    generators = {"ecdsa": gen_private_ecdsa,
                  "rsa": gen_private_rsa,
                  "dsa": gen_private_dsa
                  }
    if k not in all_privates:
        all_privates[k] = {}
    if keytype not in ["ecdsa", "dsa", "rsa"]:
        raise ValueError("Unknow private key type: %s" % keytype)
    if keytype not in all_privates[k]:
        all_privates[k][keytype] = generators[keytype]()
    return all_privates[k][keytype]


def jinja_env():
    from kpm.template_filters import jinja_filters
    jinjaenv = jinja2.Environment()
    jinjaenv.filters.update(jinja_filters())
    return jinjaenv


def jinja_template(val, env=None):
    from kpm.utils import convert_utf8
    jinjaenv = jinja_env()
    template = jinjaenv.from_string(val)
    if env is not None:
        variables = convert_utf8(json.loads(env))
    return template.render(variables)


def readfile(val):
    with open(val, 'r') as f:
        return f.read()


def jsonnet(val, env=None):
    from kpm.render_jsonnet import RenderJsonnet
    from kpm.utils import convert_utf8
    r = RenderJsonnet()
    if env is not None:
        variables = convert_utf8(json.loads(env))
    return r.render_jsonnet(val, tla_codes=variables)


def json_to_yaml(value):
    """
    Serializes an object as YAML. Optionally given keyword arguments
    are passed to yaml.dumps(), ensure_ascii however defaults to False.
    """
    return yaml.safe_dump(json.loads(value))


def json_dumps(value, **kwargs):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(value, **kwargs)


def yaml_dumps(value):
    """
    Serializes an object as YAML. Optionally given keyword arguments
    are passed to yaml.dumps(), ensure_ascii however defaults to False.
    """
    return yaml.dump(value,  default_flow_style=True)


def json_loads(value):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    return json.loads(value)


def yaml_loads(value):
    """
    Serializes an object as JSON. Optionally given keyword arguments
    are passed to json.dumps(), ensure_ascii however defaults to False.
    """
    return yaml.load(value)


def obj_loads(value):
    try:
        return json.loads(value)
    except ValueError:
        return yaml.load(value)


def jinja_filters():
    filters = {
        'json': json_dumps,
        'yaml': yaml_dumps,
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
        'read': (('filepath',), readfile),
        'hash': (('data', 'hashtype'), get_hash),
        'to_yaml': (('value',), json_to_yaml),
        'rand_alphanum': (('size', 'seed'), rand_alphanum),
        'rand_alpha': (('size', 'seed'), rand_alpha),
        'randint': (('size', 'seed'), randint),
        'jinja2': (('template', 'env'), jinja_template),
        'jsonnet': (('template', 'env'), jsonnet),
        'json_loads': (('jsonstr',), json_loads),
        'yaml_loads': (('jsonstr',), yaml_loads),
        'obj_loads': (('jsonstr',), obj_loads),
        'privatekey': (('keytype', "key", "seed"), gen_privatekey),
    }
    return filters
