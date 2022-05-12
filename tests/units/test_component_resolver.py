from typing import Iterator

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import ResolveResult, WebBrick, WebBricksConfig, web_resolver
from web_bricks.chain_forward_resolver import chain_resolver

selenium_config = WebBricksConfig(
    resolver=chain_resolver,
    locator_repr_extractor=lambda x: ' '.join([str(item) for item in x])
)

FUNC_NAME_1 = 'find_element'
FUNC_NAME_2 = 'find_elements'


def seq_gen(seq: list):
    for item in seq:
        yield item


class LogDriver:
    def __init__(self, get_element_result=None, get_elements_result=None):
        self.log = []
        self.get_element_result = get_element_result
        self.get_elements_result = get_elements_result
        self.session_id = '1'

    def find_element(self, by, value):
        self.log += [(FUNC_NAME_1, by, value)]
        if isinstance(self.get_element_result, Iterator):
            return next(self.get_element_result)
        return self.get_element_result

    def find_elements(self, by, value):
        self.log += [(FUNC_NAME_2, by, value)]
        if isinstance(self.get_elements_result, Iterator):
            return next(self.get_elements_result)
        return self.get_elements_result


def test_resolve_one():
    findable = 'gotcha'
    driver = LogDriver(get_element_result=findable)
    locator = {'by': 'css', 'value': 'any'}
    component = WebBrick(driver, locator, ResolveResult.ONE, config=selenium_config)
    assert component.resolved_element == findable


def test_resolve_one_chain():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_element_result=inner_driver)

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.ONE, config=selenium_config),
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable


def test_resolve_one_chain_with_parent_many():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_elements_result=[inner_driver])

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[0],
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable


def test_resolve_one_chain_none_result_parent():
    findable = 'gotcha'
    none_findable = None
    driver = LogDriver(get_element_result=none_findable)

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.ONE, config=selenium_config),
        another_locator,
        ResolveResult.ONE,
    )
    with pytest.raises(AssertionError):
        assert component.resolved_element == findable


def test_resolve_one_chain_none_result():
    findable = None
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_element_result=inner_driver)

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.ONE, config=selenium_config),
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable


def test_resolve_many():
    findable = 'gotcha'
    another_gotcha = 'another_gotcha'
    driver = LogDriver(get_elements_result=[findable, another_gotcha])
    locator = {'by': 'css', 'value': 'any'}
    component = WebBrick(driver, locator, ResolveResult.MANY, config=selenium_config)
    assert component.resolved_element == [findable, another_gotcha]


def test_resolve_many_none_found():
    driver = LogDriver(get_elements_result=None)
    locator = {'by': 'css', 'value': 'any'}
    component = WebBrick(driver, locator, ResolveResult.MANY, config=selenium_config)
    assert component.resolved_element == []


def test_resolve_many_len_none_found():
    driver = LogDriver(get_elements_result=None)
    locator = {'by': 'css', 'value': 'any'}
    component = WebBrick(driver, locator, ResolveResult.MANY, config=selenium_config)
    assert len(component) == 0


def test_resolve_one_chain_with_parent_many_back_index():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_elements_result=[inner_driver])

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[-1],
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable


def test_resolve_one_chain_with_parent_many_index_out_of_range():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_elements_result=[inner_driver])

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[100],
        another_locator,
        ResolveResult.ONE,
    )
    with pytest.raises(AssertionError):
        assert component.resolved_element == findable


def test_resolve_retries_one_chain_with_parent_many_index_out_of_range():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_elements_result=seq_gen([[inner_driver], [inner_driver, inner_driver]]))

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[1],
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable
    assert len(driver.log) == 2
    assert len(inner_driver.log) == 1


def test_resolve_retries_one_chain_with_parent_firstly_failed():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=None)
    another_inner_driver = LogDriver(get_element_result=findable)
    driver = LogDriver(get_elements_result=seq_gen([[inner_driver], [another_inner_driver]]))

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[0],
        another_locator,
        ResolveResult.ONE,
    )
    assert component.resolved_element == findable
    assert len(driver.log) == 2
    assert len(inner_driver.log) > 1
    assert len(another_inner_driver.log) == 1


def test_resolve_retries_many_chain_with_parent_firstly_failed():
    findable = 'gotcha'
    inner_driver = LogDriver(get_element_result=None)
    another_inner_driver = LogDriver(get_elements_result=[None, findable])
    driver = LogDriver(get_elements_result=seq_gen([[inner_driver], [another_inner_driver]]))

    one_locator = {'by': 'css', 'value': 'one_locator'}
    another_locator = {'by': 'css', 'value': 'other_locator'}

    component = WebBrick(
        WebBrick(driver, one_locator, ResolveResult.MANY, config=selenium_config)[0],
        another_locator,
        ResolveResult.MANY,
    )[1]
    assert component.resolved_element == findable
    assert len(driver.log) == 2
    assert len(inner_driver.log) > 1
    assert len(another_inner_driver.log) == 1
