from web_bricks import WebBricksConfig, WebBrick, many


def test_default_locator_extractor_get_xpath():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    assert repr(brick) == "WebBrick('/*')"


def test_default_locator_extractor_get_xpath_with_nested_brick():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    sub_brick = WebBrick(brick, '//*/[atr="asdasd"]')
    assert repr(sub_brick) == """WebBrick('/*//*/[atr="asdasd"]')"""


def test_default_locator_extractor_get_xpath_with_nested_many_brick():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    sub_brick = many(WebBrick(brick, '//*/[atr="asdasd"]'))
    assert repr(sub_brick) == """WebBrick[]('/*//*/[atr="asdasd"]')"""


def test_default_locator_extractor_get_xpath_of_one_of_nested_many_brick():
    conf = WebBricksConfig()
    brick = WebBrick(None, '/*', config=conf)
    sub_brick = many(WebBrick(brick, '//*/[atr="asdasd"]'))[0]
    assert repr(sub_brick) == """WebBrick('(/*//*/[atr="asdasd"])[0]')"""


def test_fuckup_default_locator_on_root_many():
    conf = WebBricksConfig()
    brick = many(WebBrick(None, '/*', config=conf))
    assert repr(brick) == """WebBrick[]('/*')"""


def test_fuckup_default_locator_on_root_one_of_many():
    conf = WebBricksConfig()
    brick = many(WebBrick(None, '/*', config=conf))[0]
    assert repr(brick) == """WebBrick('(/*)[0]')"""
