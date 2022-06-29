from functools import reduce
from typing import Iterator

from web_bricks import (ResolveResult, ResolverInputSet, WebBrick,
                        WebBricksConfig, many)
from web_bricks.component import IndexLocator


class DriverSim:
    @property
    def text(self):
        return 1

    def click(self):
        pass


FUNC_NAME_1 = 'querySelector'
FUNC_NAME_2 = 'querySelectorAll'


class LogDriver:
    def __init__(self, get_element_result=None, get_elements_result=None):
        self.log = []
        self.get_element_result = get_element_result
        self.get_elements_result = get_elements_result
        self.session_id = '1'

    def querySelector(self, locator):
        self.log += [(FUNC_NAME_1, locator)]
        if isinstance(self.get_element_result, Iterator):
            return next(self.get_element_result)
        return self.get_element_result

    def querySelectorAll(self, locator):
        self.log += [(FUNC_NAME_2, locator)]
        if isinstance(self.get_elements_result, Iterator):
            return next(self.get_elements_result)
        return self.get_elements_result


def resolver(resolver_input_set: ResolverInputSet):
    func = {
        ResolveResult.ONE: 'querySelector',
        ResolveResult.MANY: 'querySelectorAll'
    }[resolver_input_set.strategy]

    elm = None
    try:
        elm = getattr(resolver_input_set.driver, func)(resolver_input_set.full_locator)
    except:  # noqa
        pass
    return elm


def locator_func(path):
    def reducer(full_path, locator):
        if full_path is None:
            return f'{locator["xpath"]}'

        if isinstance(locator, IndexLocator):
            return f'({full_path})[{locator.index}]'

        return f'{full_path}{locator["xpath"]}'

    return reduce(reducer, path, None)


# TODO наименование
def test_one_type_locators_to_xpath():
    conf = WebBricksConfig(
        resolver=resolver,
        locator_repr_extractor=locator_func
    )

    res = 'value'
    driver = LogDriver(get_element_result=res)

    brick = WebBrick(driver, {'xpath': ''}, config=conf)
    sub_brick = WebBrick(brick, {'xpath': '//*[@data-n="wat-search-results-list"]'})
    sub_sub_brick = WebBrick(sub_brick, {'xpath': '//*[@data-n="wat-minicard"]'})
    assert sub_sub_brick.resolved_element == res


# TODO наименование
def test_many_indexed_type_locators_to_xpath_to_one_resolved():
    conf = WebBricksConfig(
        resolver=resolver,
        locator_repr_extractor=locator_func
    )

    res = 'value'
    driver = LogDriver(
        get_element_result=res,
        get_elements_result=[res]
    )

    brick = WebBrick(driver, {'xpath': ''}, config=conf)
    sub_brick = WebBrick(brick, {'xpath': '//*[@data-n="wat-search-results-list"]'})
    sub_sub_brick = many(WebBrick(sub_brick, {'xpath': '//*[@data-n="wat-minicard"]'}))[0]
    assert sub_sub_brick.resolved_element == res


# TODO наименование
def test_many_type_locators_to_xpath_to_array_resolved():
    conf = WebBricksConfig(
        resolver=resolver,
        locator_repr_extractor=locator_func
    )

    res = 'value'
    driver = LogDriver(
        get_element_result=res,
        get_elements_result=[res]
    )

    brick = WebBrick(driver, {'xpath': ''}, config=conf)
    sub_brick = WebBrick(brick, {'xpath': '//*[@data-n="wat-search-results-list"]'})
    sub_sub_brick = many(WebBrick(sub_brick, {'xpath': '//*[@data-n="wat-minicard"]'}))
    assert sub_sub_brick.resolved_element == [res]
