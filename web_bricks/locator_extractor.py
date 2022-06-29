from functools import reduce

from .index_locator import IndexLocator


def default_str_locator_extractor(path):
    def reducer(full_path, locator):
        if full_path is None:
            return f'{locator}'

        if isinstance(locator, IndexLocator):
            return f'({full_path})[{locator.index}]'

        return f'{full_path}{locator}'

    return reduce(reducer, path, None)
