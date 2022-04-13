from functools import reduce

from web_bricks import ResolverInputSet, WebBrick, WebBricksConfig, many
from web_bricks.component import IndexLocator


def resolver(resolver_input_set: ResolverInputSet):
    pass


class DriverSim:
    @property
    def text(self):
        return 1

    def click(self):
        pass


def locator_func(path):
    def reducer(full_path, locator):
        if isinstance(locator, IndexLocator):
            return f'({full_path})[{locator.index}]'

        if isinstance(full_path, dict):
            full_path = full_path['xpath']
        return full_path + locator['xpath']

    return reduce(reducer, path)


def test_one_type_locators_to_xpath():
    conf = WebBricksConfig(
        resolver=resolver,
        locator_repr_extractor=locator_func
    )

    driver = DriverSim()

    brick = WebBrick(driver, {'xpath': ''}, config=conf)
    sub_brick = WebBrick(brick, {'xpath': '//*[@data-n="wat-search-results-list"]'})
    sub_sub_brick = many(WebBrick(sub_brick, {'xpath': '//*[@data-n="wat-minicard"]'}))[1]
    assert repr(sub_sub_brick) \
           == '''WebBrick('(//*[@data-n="wat-search-results-list"]//*[@data-n="wat-minicard"])[1]')'''


def another_locator_func(path):
    def reducer(full_path, locator):
        if isinstance(locator, IndexLocator):
            return f'{full_path} [{locator.index}]'

        if isinstance(full_path, dict):
            full_path = full_path['value']
        return f'{full_path} {locator["value"]}'

    return reduce(reducer, path)


def test_another_type_locators_to_css():
    conf = WebBricksConfig(
        resolver=resolver,
        locator_repr_extractor=another_locator_func
    )

    driver = DriverSim()

    brick = WebBrick(driver, {'by': 'css', 'value': ':root'}, config=conf)
    sub_brick = WebBrick(brick, {'by': 'css', 'value': '[data-n="wat-search-results-list"]'})
    sub_sub_brick = many(WebBrick(sub_brick, {'by': 'css', 'value': '[data-n="wat-minicard"]'}))[1]
    assert repr(sub_sub_brick) == '''WebBrick(':root [data-n="wat-search-results-list"] [data-n="wat-minicard"] [1]')'''
