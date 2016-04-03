import pytest
from kpm.kubernetes import get_endpoint, Kubernetes


NAMESPACE="testns"


resource_endpoints = {
    "daemonsets": "/apis/extensions/v1beta1/namespaces/testns/daemonsets",
    "deployments": "/apis/extensions/v1beta1/namespaces/testns/deployments",
    "horizontalpodautoscalers": "/apis/extensions/v1beta1/namespaces/testns/horizontalpodautoscalers",
    "ingresses": "/apis/extensions/v1beta1/namespaces/testns/ingresses",
    "jobs": "/apis/extensions/v1beta1/namespaces/testns/jobs",
    "namespaces": "/api/v1/namespaces",
    "replicasets": "/apis/extensions/v1beta1/namespaces/testns/replicasets",
    "persistentvolumes": "/api/v1/namespaces/testns/persistentvolumes",
    "persistentvolumeclaims": "/api/v1/namespaces/testns/persistentvolumeclaims",
    "services": "/api/v1/namespaces/testns/services",
    "serviceaccounts": "/api/v1/namespaces/testns/serviceaccounts",
    "configmaps": "/api/v1/namespaces/testns/configmaps",
    "replicationcontrollers": "/api/v1/namespaces/testns/replicationcontrollers",
}


def test_endpoints():
    a = get_endpoint("po")
    b = get_endpoint("pods")
    c = get_endpoint("pod")
    assert a == b
    assert b == c


def test_endpoints_missing():
    with pytest.raises(KeyError):
        get_endpoint("bad")
