from typing import Iterator

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import ResolveResult, web_resolver

web_driver_resolver = web_resolver(waiter=WebDriverWait, ignored_exceptions=(TimeoutException,), timeout=3)

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
    assert web_driver_resolver(driver, locator, ResolveResult.ONE) == findable
    assert driver.log == [(FUNC_NAME_1, locator['by'], locator['value'])]


def test_retry_resolve_one():
    findable = 'gotcha'
    driver = LogDriver(get_element_result=seq_gen([None, findable]))
    locator = {'by': 'css', 'value': 'any'}
    assert web_driver_resolver(driver, locator, ResolveResult.ONE) == findable
    assert driver.log == [(FUNC_NAME_1, locator['by'], locator['value'])] * 2


def test_retry_exhausted_resolve_one():
    driver = LogDriver(get_element_result=seq_gen([None] * 100))
    locator = {'by': 'css', 'value': 'any'}
    assert web_driver_resolver(driver, locator, ResolveResult.ONE) == None  # noqa: E711
    assert (FUNC_NAME_1, locator['by'], locator['value']) in driver.log
    assert len(driver.log) > 2


def test_resolve_many():
    findable = 'gotcha'
    driver = LogDriver(get_elements_result=findable)
    locator = {'by': 'css', 'value': 'any'}
    assert web_driver_resolver(driver, locator, ResolveResult.MANY) == findable
    assert driver.log == [(FUNC_NAME_2, locator['by'], locator['value'])]
