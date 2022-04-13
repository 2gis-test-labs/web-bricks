from .acesss_logger import ResolutionErrorLog, stdout_logger
from .index_locator import IndexLocator
from .resolve_result import ResolveResult
from .resolver_interface import ResolverInputSet


class NonexistingException(BaseException):
    pass


def web_resolver(waiter, ignored_exceptions=None, timeout=None, logger=stdout_logger, log_action=ResolutionErrorLog):
    if ignored_exceptions is None:
        ignored_exceptions = NonexistingException

    def resolver(resolution_input_set: ResolverInputSet):
        parent_element = resolution_input_set.parent
        locator = resolution_input_set.locator
        driver_resolve_func = resolution_input_set.strategy
        assert timeout is not None, 'Не установлен таймаут для поиска элемента на странице'

        selenium_func = {
            ResolveResult.ONE: 'find_element',
            ResolveResult.MANY: 'find_elements'
        }

        elm = None
        if isinstance(locator, IndexLocator):
            try:
                elm = parent_element[locator.index]
            except IndexError as e:
                logger(log_action(parent_element, locator, e))
            return elm

        try:
            wait = waiter(parent_element, timeout)
            elm = wait.until(lambda dr: object.__getattribute__(dr, selenium_func[driver_resolve_func])(**locator))
        except ignored_exceptions as e:
            logger(log_action(parent_element, locator, e))

        return elm

    return resolver
