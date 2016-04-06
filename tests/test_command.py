from kpm.command import get_parser


# Real-test are in test_integration
def test_get_parser():
    parser = get_parser()
    assert parser is not None
