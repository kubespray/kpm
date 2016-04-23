import pytest
from kpm.console import KubernetesExec


def test_console_default():
    k = KubernetesExec("myrc", "echo titi")
    assert k is not None
