from functools import reduce

import pytest
from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import ResolveResult, WebBrick, ResolverInputSet
from web_bricks.component import SafetyUsageError
from web_bricks.index_locator import IndexLocator
from web_bricks.resolver import web_resolver
from web_bricks.web_bricks_config import WebBricksConfig


def another_locator_func(path):
    print('p', path)

    def reducer(full_path, locator):
        print('red', full_path, locator)
        if full_path is None:
            return f'{locator["value"]}'

        if isinstance(locator, IndexLocator):
            return f'{full_path} {locator.index}'

        return f'{full_path} {locator["value"]}'

    return reduce(reducer, path, None)


selenium_config = WebBricksConfig(
    resolver=web_resolver(waiter=WebDriverWait, timeout=1),
    locator_repr_extractor=another_locator_func,
)


def find_by_attr(name):
    locator = '[data-n="%s"]' % name
    return {'by': 'css selector', 'value': locator}


def test_repr_one():
    locator = find_by_attr(name='some_locator')
    component = WebBrick(None, locator, ResolveResult.ONE, config=selenium_config)
    assert repr(component) == f"WebBrick('{locator['value']}')"


def test_repr_one_inherrit():
    locator = find_by_attr(name='some_locator')

    class RootPage(WebBrick):
        pass

    component = RootPage(None, locator, ResolveResult.ONE, config=selenium_config)
    assert repr(component) == f"RootPage('{locator['value']}')"


def test_repr_one_chain():
    inner_locator = find_by_attr(name='one')
    outer_locator = find_by_attr(name='another')
    component = WebBrick(
        WebBrick(None, inner_locator, ResolveResult.ONE, config=selenium_config),
        outer_locator,
        ResolveResult.ONE
    )
    assert repr(component) == f"WebBrick('{inner_locator['value']} {outer_locator['value']}')"


def test_repr_one_chain_inherit():
    inner_locator = find_by_attr(name='one')
    outer_locator = find_by_attr(name='another')

    class RootPage(WebBrick):
        pass

    class SubPage(WebBrick):
        pass

    component = SubPage(
        RootPage(None, inner_locator, ResolveResult.ONE, config=selenium_config),
        outer_locator,
        ResolveResult.ONE
    )
    assert repr(component) == f"SubPage('{inner_locator['value']} {outer_locator['value']}')"


def test_repr_many():
    locator = {'by': 'index', 'value': 'any_locator'}
    component = WebBrick(None, locator, ResolveResult.MANY, config=selenium_config)
    assert repr(component) == f"WebBrick[]('{locator['value']}')"


def test_repr_many_inherit():
    locator = {'by': 'index', 'value': 'any_locator'}

    class RootPage(WebBrick):
        pass

    component = RootPage(None, locator, ResolveResult.MANY, config=selenium_config)
    assert repr(component) == f"RootPage[]('{locator['value']}')"


def test_repr_list():
    locator = {'by': 'index', 'value': 'any_locator'}
    component = WebBrick(None, locator, config=selenium_config).list()
    assert repr(component) == f"WebBrick[]('{locator['value']}')"


def test_repr_one_of_many():
    locator = {'by': 'index', 'value': 'any_locator'}
    component = WebBrick(None, locator, ResolveResult.MANY, config=selenium_config)
    assert repr(component[2]) == f"WebBrick('{locator['value']} 2')"


class LogDriver:
    def __init__(self):
        self.log = []

    def get_element(self, locator):
        self.log += [('get_element', locator)]

    def get_elements(self, locator):
        self.log += [('get_elements', locator)]


class LogResolver:
    def __init__(self, value='gotcha'):
        self.log = []
        self.value = value

    def resolve(self, resolver_input_set: ResolverInputSet):
        driver = resolver_input_set.parent
        locator = resolver_input_set.locator
        strategy = resolver_input_set.strategy
        self.log += [(driver, locator, strategy)]
        return self.value


def test_no_action_resolution():
    locator = find_by_attr(name='some_locator')
    resolver = LogResolver()
    WebBrick(None, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert resolver.log == []


def test_no_action_many_index():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    WebBrick(driver, locator, ResolveResult.MANY, config=selenium_config, resolver=resolver.resolve)[0]
    assert resolver.log == []


def test_action_one_resolution():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve).resolved_element
    assert resolver.log == [(driver, locator, ResolveResult.ONE)]


def test_action_one_resolution_none_result():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(None)
    WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve).resolved_element
    assert resolver.log == [(driver, locator, ResolveResult.ONE)] * 3


def test_action_many_resolution():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    WebBrick(driver, locator, ResolveResult.MANY, config=selenium_config, resolver=resolver.resolve).resolved_element
    assert resolver.log == [(driver, locator, ResolveResult.MANY)]


def test_index_for_one():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    with pytest.raises(AssertionError):
        WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)[0]
    assert resolver.log == []


def test_index_out_of_range_for_one():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    with pytest.raises(AssertionError):
        WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)[1000]
    assert resolver.log == []


def test_try_iter_for_one():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    with pytest.raises(AssertionError):
        for item in WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve):
            pass
    assert resolver.log == []


def test_equality_of_value():
    the_value = 'gotcha'
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert (component == the_value) is True
    assert resolver.log == [(driver, locator, ResolveResult.ONE)]


def test_equality_of_value_of_none():
    the_none_value = None
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_none_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert (component == the_none_value) is True
    assert len(resolver.log) > 2


def test_unequality_of_value_with_none():
    the_value = 'gotcha'
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert (component != None) is True  # noqa: E711
    assert resolver.log == [(driver, locator, ResolveResult.ONE)]


def test_unequality_of_value_of_none_with_data():
    the_none_value = None
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_none_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert (component != 'some value') is True
    assert len(resolver.log) > 2


def test_equality_of_same():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    with pytest.raises(AssertionError):
        assert (component == component) is False


def test_non_equality_of_same():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    with pytest.raises(AssertionError):
        assert (component != component) is False


def test_equality_of_different_web_bricks_same_value():
    the_value = 'gotcha'
    driver = LogDriver()

    locator = find_by_attr(name='some_locator')
    resolver = LogResolver(the_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)

    another_locator = find_by_attr(name='another_locator')
    another_resolver = LogResolver(the_value)
    another_component = WebBrick(
        driver, another_locator, ResolveResult.ONE, config=selenium_config, resolver=another_resolver.resolve
    )
    assert (component == another_component) is True


def test_equality_of_different_web_bricks_different_values():
    driver = LogDriver()

    value = 'gotcha'
    locator = find_by_attr(name='some_locator')
    resolver = LogResolver(value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)

    another_value = 'achtog'
    another_locator = find_by_attr(name='another_locator')
    another_resolver = LogResolver(another_value)
    another_component = WebBrick(
        driver, another_locator, ResolveResult.ONE, config=selenium_config, resolver=another_resolver.resolve
    )
    assert (component == another_component) is False


def test_assertion_on_component_with_value():
    the_value = 'gotcha'
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    with pytest.raises(SafetyUsageError):
        assert component
    assert resolver.log == []


def test_assertion_on_component_with_none():
    the_none_value = None
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver(the_none_value)
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    with pytest.raises(SafetyUsageError):
        assert component
    assert resolver.log == []


def test_root_brick_for_one():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    brick = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert id(brick.root_brick()) == id(brick)


def test_driver_for_one():
    locator = find_by_attr(name='some_locator')
    driver = LogDriver()
    resolver = LogResolver()
    brick = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config, resolver=resolver.resolve)
    assert id(brick.driver) == id(driver)
