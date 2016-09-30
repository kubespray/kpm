import os


class Config(object):
    """ Default configuration """
    DEBUG = False
    KUBE_APIMASTER = os.getenv('KUBE_APIMASTER', 'http://localhost:8001')
    KPM_URI = os.getenv('KPM_URI', "http://localhost:5000")
    CNR_URI = os.getenv('CNR_URI', KPM_URI)
    KPM_REGISTRY_HOST = os.getenv('KPM_REGISTRY_HOST', KPM_URI)
    KPM_BUILDER_HOST = os.getenv('KPM_BUILDER_HOST', KPM_URI)
    CNR_MODELS_MODULE = os.getenv('KPM_MODELS_MODULE', "cnr.models.etcd")
    CNR_MODELS = os.getenv('KPM_MODELS', '{"Package": "cnr.models.etcd.package:Package"}')
    KPM_API_BACKEND = 'true'
    KPM_API_BUILDER = 'true'
    KPM_API_REGISTRY = 'true'


class ProductionConfig(Config):
    """ Production configuration """
    KPM_URI = "http://localhost:5000"
    CNR_URI = os.getenv('CNR_URI', KPM_URI)
    KPM_BACKEND = 'false'


class DevelopmentConfig(Config):
    """ Development configuration """
    DEBUG = True
#    KPM_URI = 'https://api.kpm.sh'
    KPM_URI = os.getenv('KPM_URI', "http://localhost:5000")
    CNR_URI = os.getenv('CNR_URI', KPM_URI)
