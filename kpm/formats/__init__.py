from kpm.formats.kubcompose import KubCompose
from kpm.formats.kub import Kub


kub_formats = [Kub, KubCompose]
kub_by_name = {k.media_type: k for k in kub_formats}
kub_by_platforms = {k.platform: k for k in kub_formats}


def kub_factory(name, *args, **kwargs):
    kub_class = kub_by_name[name]
    target = kwargs.pop('convert_to', None)
    k = kub_class(*args, **kwargs)
    if target is not None and target != kub_class.target:
        k = k.convert_to(target)
    return k
