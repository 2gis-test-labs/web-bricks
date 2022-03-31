from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import ResolveResult, WebBrick, WebBricksConfig, web_resolver


def find_by_attr(name):
    locator = '[data-n="%s"]' % name
    return {'by': 'css selector', 'value': locator}


def test_base_class_repr_chain():
    selenium_config = WebBricksConfig(
        resolver=web_resolver(waiter=WebDriverWait, timeout=1),
        locator_repr_extractor=lambda x: x['value'],
    )

    class RootPage(WebBrick):
        pass

    class SubPage(WebBrick):
        pass

    locator = find_by_attr(name='some_locator')
    another_locator = find_by_attr(name='another_locator')
    component = SubPage(
        RootPage(None, locator, ResolveResult.ONE, config=selenium_config),
        another_locator,
        ResolveResult.ONE
    )
    assert repr(component) == f"SubPage('{locator['value']} {another_locator['value']}')"


def test_custom_class_repr_chain():
    selenium_config = WebBricksConfig(
        resolver=web_resolver(waiter=WebDriverWait, timeout=1),
        locator_repr_extractor=lambda x: x['value'],
        class_name_repr_func=lambda x: '.'.join(x.class_full_path)
    )

    class RootPage(WebBrick):
        pass

    class SubPage(WebBrick):
        pass

    locator = find_by_attr(name='some_locator')
    another_locator = find_by_attr(name='another_locator')
    component = SubPage(
        RootPage(None, locator, ResolveResult.ONE, config=selenium_config),
        another_locator,
        ResolveResult.ONE
    )
    assert repr(component) == f"RootPage.SubPage('{locator['value']} {another_locator['value']}')"
