from typing import List

from rtry import retry

from .index_locator import IndexLocator
from .resolve_result import ResolveResult

from .web_bricks_config import WebBricksConfig


class SafetyUsageError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class WebBrick:
    def __init__(self, parent_element, locator, driver_func=ResolveResult.ONE,
                 config: WebBricksConfig = None, resolver=None, logger=None):
        assert isinstance(parent_element, WebBrick) or config is not None, SafetyUsageError(
            f'Узел {self.__class__} прикрепляется не к дереву Component-ов, '
            f'а к драйверу parent_element={parent_element} '
            f'или забыли указать конфигурацию для корневого элемента в свойстве config={config}'
        )
        self.parent_element = parent_element
        self._locator = locator
        self._resolver = resolver
        self._driver_resolve_func_name = driver_func
        self.session_id = 'WebBrick plug session_id'
        self.config = config
        self._logger = logger

    def _parent_path(self) -> list:
        if isinstance(self.parent_element, WebBrick):
            return self.parent_element._full_path()
        return []

    def _full_path(self) -> list:
        return self._parent_path() + [self._locator]

    @property
    def locator_full_path(self):
        if not hasattr(self, '_locator_full_path_cache'):
            self._locator_full_path_cache = self._full_path()
        return self._locator_full_path_cache

    def locator_full_str_path(self):
        return self.get_root_config().locator_repr_extractor(self.locator_full_path)

    def _parent_class_path(self) -> list:
        if isinstance(self.parent_element, WebBrick):
            return self.parent_element._class_full_path()
        return []

    def _class_full_path(self) -> list:
        return self._parent_class_path() + [self.__class__.__name__]

    @property
    def class_full_path(self):
        if not hasattr(self, '_class_full_path_cache'):
            self._class_full_path_cache = self._class_full_path()
        return self._class_full_path_cache

    def __repr__(self):
        class_full_path = self.get_root_config().class_name_repr_func(self)
        locator_full_path = self.locator_full_str_path()

        many = '[]' if self._driver_resolve_func_name == ResolveResult.MANY else ''
        return f"{class_full_path}{many}('{locator_full_path}')"

    @property
    def _resolved_parent(self):
        parent_element = self.parent_element
        if isinstance(self.parent_element, WebBrick):
            parent_element = self.parent_element._resolved_current
            assert parent_element is not None, \
                f'Не найден родительский элемент {self.parent_element} для {self.__class__}:{self}'
        return parent_element

    @property
    def _resolved_current(self):
        parent_element = self._resolved_parent
        resolver = self._resolver if self._resolver else self.get_root_config().resolver
        return resolver(parent_element, self._locator, self._driver_resolve_func_name)

    @property  # type: ignore
    @retry(attempts=3, until=lambda x: x is None, swallow=AssertionError)
    def resolved_element(self):
        result = self._resolved_current
        self.log(self.get_root_config().resolution_log(self, result))
        if result is None and self._driver_resolve_func_name == ResolveResult.MANY:
            result = []
        return result

    def resolved_found_element(self, fail_msg='нет элемента на странице'):
        result = self.resolved_element
        assert (result is not None) and (result != []), f'Не нашли элемент {self}: {fail_msg}'
        return result

    def root_brick(self) -> 'WebBrick':
        parent_element = self.parent_element
        if not isinstance(parent_element, WebBrick):
            return self
        return parent_element.root_brick()

    def get_root_config(self) -> WebBricksConfig:
        root_brick = self.root_brick()
        root_brick_config = root_brick.config
        assert root_brick_config is not None, SafetyUsageError(
            f'Корневой элемент {self.__class__} должен содержать '
            f'конфиг с стратегией {root_brick.config} для поиска элементов'
        )
        # TODO cache config?
        return root_brick_config

    def log(self, record):
        self.get_root_config().logger(record)

    @property
    def driver(self):
        return self.root_brick().parent_element

    def __len__(self):
        assert self._driver_resolve_func_name == ResolveResult.MANY, SafetyUsageError(
            f'Попытка обратиться за длиной массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )
        result = self.resolved_element
        if result is None:
            result = []
        return len(result)

    def __getitem__(self, item):
        assert self._driver_resolve_func_name == ResolveResult.MANY, SafetyUsageError(
            f'Попытка обратиться к элементу массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )

        return self.__class__(
            parent_element=self,
            locator=IndexLocator(item),
        )

    def __iter__(self):
        assert self._driver_resolve_func_name == ResolveResult.MANY, SafetyUsageError(
            f'Попытка итерировать элементы массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )
        return iter([self[idx] for idx in range(len(self))])

    def list(self) -> List:
        self._driver_resolve_func_name = ResolveResult.MANY
        return self  # type: ignore  # WebBrick реализует интерфейс List

    def is_equal(self, other):
        if isinstance(other, WebBrick):
            assert repr(self) != repr(other), SafetyUsageError(
                f'Сравнение описаний {self.__class__} не равносильно сравнению значений элементов. '
                f'Сравнение компонента с собой {self} всегда будет приводить к успешному результату'
            )
            return self.resolved_element is other.resolved_element
        return self.resolved_element is other

    def __eq__(self, other):
        # TODO стоит добавить __ne__, что бы корректно прокинуть not в проверки
        return self.is_equal(other)

    def __bool__(self):
        raise SafetyUsageError(
            f'Взаимодействие осуществляется с описанием элемента {self.__class__}, а не '
            f'с элементом страницы {self}, для проверки свойств используй методы и обращения к свойствам'
        )
