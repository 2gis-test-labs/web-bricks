from rtry import retry

from .component import WebBrick
from .index_locator import IndexLocator
from .resolve_result import ResolveResult


def resolver(parent_element, locator, driver_resolve_func, logger, ignored_exceptions):
    selenium_func = {
        ResolveResult.ONE: 'find_element',
        ResolveResult.MANY: 'find_elements'
    }

    elm = None
    if isinstance(locator, IndexLocator):
        try:
            elm = parent_element[locator.index]
        except IndexError:
            pass
        return elm

    elm = retry(swallow=ignored_exceptions, attempts=10, until=lambda x: x is None)(
        lambda: object.__getattribute__(parent_element, selenium_func[driver_resolve_func])(**locator)
    )()

    return elm


def chain_resolver(web_brick):
    parent_element = web_brick.parent
    if isinstance(parent_element, WebBrick):
        parent_element = chain_resolver(parent_element)
        assert parent_element is not None, \
            f'Не найден родительский элемент {web_brick._parent_element} для {web_brick.__class__}:{web_brick}'

    result = resolver(parent_element, web_brick.locator, web_brick.strategy, web_brick.logger,
                      ignored_exceptions=BaseException)
    if result is None and web_brick.strategy == ResolveResult.MANY:
        result = []
    return result
