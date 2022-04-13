from .acesss_logger import ResolutionErrorLog, stdout_logger
from .index_locator import IndexLocator
from .resolve_result import ResolveResult


class NonexistingException(BaseException):
    pass


def web_resolver(waiter, ignored_exceptions=None, timeout=None, logger=stdout_logger, log_action=ResolutionErrorLog):
    if ignored_exceptions is None:
        ignored_exceptions = NonexistingException

    def resolver(parent_element, locator: dict, driver_resolve_func):
        assert timeout is not None, 'Не установлен таймаут для поиска элемента на странице'

        selenium_func = {
            ResolveResult.ONE: 'find_element',
            ResolveResult.MANY: 'find_elements'
        }

        elm = None
        try:
            wait = waiter(parent_element, timeout)
            elm = wait.until(lambda dr: object.__getattribute__(dr, selenium_func[driver_resolve_func])(**locator))
        except ignored_exceptions as e:
            logger(log_action(parent_element, locator, e))

        return elm

    return resolver


def index_resolver(element_type, logger=stdout_logger, log_action=ResolutionErrorLog):
    def index_resolver(elements, locator: IndexLocator, driver_resolve_func) -> element_type:
        index = locator.index
        element = None
        try:
            element = elements[index]
        except IndexError as e:
            logger(log_action(elements, locator, e))
        return element

    return index_resolver
