from .acesss_logger import ResolutionErrorLog, ResolutionLog, stdout_logger


def _value_getter(x):
    return x['value']


class WebBricksConfig:
    def __init__(self, resolver=None, locator_repr_extractor=None, logger=None,
                 root_locator=None, resolution_log=None, resolution_log_error=None, class_name_repr_func=None):

        if resolver is None:
            resolver = lambda web_brick: web_brick
        self.resolver = resolver

        if root_locator is None:
            root_locator = {'by': 'css', 'value': ':root'}
        self.root_locator = root_locator

        if locator_repr_extractor is None:
            locator_repr_extractor = _value_getter
        self.locator_repr_extractor = locator_repr_extractor

        if logger is None:
            logger = stdout_logger
        self.logger = logger

        if resolution_log is None:
            resolution_log = ResolutionLog
        self.resolution_log = resolution_log

        if resolution_log_error is None:
            resolution_log_error = ResolutionErrorLog
        self.resolution_log_error = resolution_log_error

        if class_name_repr_func is None:
            def only_name_class(x):
                return x.__class__.__name__

            class_name_repr_func = only_name_class
        self.class_name_repr_func = class_name_repr_func
