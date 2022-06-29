import pytest

from web_bricks import WebBricksConfig, WebBrick, many
from web_bricks.safety_error import SafetyUsageError


def test_disabled_default_resolver_on_array():
    conf = WebBricksConfig()
    brick = many(WebBrick(None, '/*', config=conf))
    with pytest.raises(SafetyUsageError):
        len(brick)


def test_disabled_default_resolver_on_eq():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    with pytest.raises(SafetyUsageError):
        brick == 1


def test_disabled_default_resolver_on_assert():
    conf = WebBricksConfig()
    brick = many(WebBrick(None, '/*', config=conf))
    with pytest.raises(SafetyUsageError):
        assert brick


def test_disabled_default_resolver_on_resolve():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    with pytest.raises(SafetyUsageError):
        assert brick.resolved()


def test_disabled_default_resolver_on_resolve_element_legacy():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    with pytest.raises(SafetyUsageError):
        assert brick.resolved_element()


def test_disabled_default_resolver_on_iter():
    conf = WebBricksConfig()
    brick = many(WebBrick(None, '/*', config=conf))
    with pytest.raises(SafetyUsageError):
        for item in brick:
            pass
