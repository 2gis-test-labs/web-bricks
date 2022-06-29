from functools import reduce

from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import ResolveResult, WebBrick, WebBricksConfig, web_resolver
from web_bricks.index_locator import IndexLocator


def find_by_attr(name):
    locator = '[data-n="%s"]' % name
    return {'by': 'css selector', 'value': locator}


def another_locator_func(path):
    def reducer(full_path, locator):
        if isinstance(locator, IndexLocator):
            return f'{full_path} [{locator.index}]'

        if isinstance(full_path, dict):
            full_path = full_path['value']
        return f'{full_path} {locator["value"]}'

    return reduce(reducer, path)


def test_base_class_repr_chain():
    selenium_config = WebBricksConfig(
        resolver=web_resolver(waiter=WebDriverWait, timeout=1),
        locator_repr_extractor=another_locator_func,
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
        locator_repr_extractor=another_locator_func,
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
