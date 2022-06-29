from typing import List

from rtry import retry

from .index_locator import IndexLocator
from .resolve_result import ResolveResult
from .safety_error import SafetyUsageError
from .web_bricks_config import WebBricksConfig


class WebBrick:
    """
    WebBrick - цепочечный локатор элемента

    Props:
        *driver* - объект web драйвера/браузера\n
        *parent* - web_brick - родительский локатор элемента\n
        *locator* - текущий локатор элемента\n
        *full_locator* - массив локаторов элемента упорядоченные по вложенности\n
        *full_locator_str* - строка полного локатора элемента
        *strategy* - стратегия выборки элемента (например простая - один много)\n
        *resolved* - свойство для вызова WebBricksConfig.resolver(self: WebBrick)\n
    """

    LOCATOR = None

    def __init__(self, parent_element, locator=None, strategy=ResolveResult.ONE, config: WebBricksConfig = None):
        assert isinstance(parent_element, WebBrick) or config is not None, SafetyUsageError(
            f'Узел {self.__class__} прикрепляется не к дереву Component-ов, '
            f'а к драйверу parent_element={parent_element} '
            f'или забыли указать конфигурацию для корневого элемента в свойстве config={config}'
        )
        self._parent_element = parent_element

        self._locator = self.LOCATOR
        if locator:
            self._locator = locator

        self._config = config
        self._strategy = strategy
        self.session_id = 'WebBrick plug session_id'

    def _parent_path(self) -> list:
        if isinstance(self._parent_element, WebBrick):
            return self._parent_element._full_path()
        return []

    def _full_path(self) -> list:
        return self._parent_path() + [self._locator]

    @property
    def strategy(self):
        return self._strategy

    @property
    def locator(self):
        return self._locator

    @property
    def full_locator(self):
        if not hasattr(self, '_locator_full_path_cache'):
            self._locator_full_path_cache = self._full_path()
        return self._locator_full_path_cache

    @property
    def full_locator_str(self):
        return self.config.locator_repr_extractor(self.full_locator)

    def _parent_class_path(self) -> list:
        if isinstance(self._parent_element, WebBrick):
            return self._parent_element._class_full_path()
        return []

    def _class_full_path(self) -> list:
        return self._parent_class_path() + [self.__class__.__name__]

    @property
    def class_full_path(self):
        DeprecationWarning('class_full_path is deprecated')
        if not hasattr(self, '_class_full_path_cache'):
            self._class_full_path_cache = self._class_full_path()
        return self._class_full_path_cache

    def __repr__(self):
        class_full_path = self.config.class_name_repr_func(self)
        locator_full_path = self.full_locator_str

        many = '[]' if self._strategy == ResolveResult.MANY else ''
        return f"{class_full_path}{many}('{locator_full_path}')"

    @property  # type: ignore
    @retry(attempts=3, until=lambda x: x is None, swallow=AssertionError)
    def resolved_element(self):
        DeprecationWarning('resolved_element deprecated, use resolved instead')
        return self.config.resolver(self)

    @property
    @retry(attempts=3, until=lambda x: x is None, swallow=AssertionError)
    def resolved(self):
        return self.config.resolver(self)

    def _root_brick(self) -> 'WebBrick':
        parent_element = self._parent_element
        if not isinstance(parent_element, WebBrick):
            return self
        return parent_element._root_brick()

    @property
    def config(self) -> WebBricksConfig:
        root_brick = self._root_brick()
        root_brick_config = root_brick._config
        assert root_brick_config is not None, SafetyUsageError(
            f'Корневой элемент {self.__class__} должен содержать '
            f'конфиг с стратегией {root_brick._config} для поиска элементов'
        )
        # TODO cache config?
        return root_brick_config

    def logger(self, record):
        self.config.logger(record)

    @property
    def driver(self):
        return self._root_brick()._parent_element

    @property
    def parent(self):
        return self._parent_element

    def __len__(self):
        assert self._strategy == ResolveResult.MANY, SafetyUsageError(
            f'Попытка обратиться за длиной массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )
        result = self.resolved_element
        if result is None:
            result = []
        return len(result)

    def __getitem__(self, item):
        assert self._strategy == ResolveResult.MANY, SafetyUsageError(
            f'Попытка обратиться к элементу массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )

        return self.__class__(
            parent_element=self,
            locator=IndexLocator(item),
        )

    def __iter__(self):
        assert self._strategy == ResolveResult.MANY, SafetyUsageError(
            f'Попытка итерировать элементы массива компонентов в {self.__class__}, '
            f'но в определении указан одиночный веб-элемент, '
            'возможно забыли добавить many? - many( WebBrick(...) )'
        )
        return iter([self[idx] for idx in range(len(self))])

    def list(self) -> List:
        self._strategy = ResolveResult.MANY
        return self  # type: ignore  # WebBrick реализует интерфейс List

    def _is_equal(self, other):
        if isinstance(other, WebBrick):
            assert repr(self) != repr(other), SafetyUsageError(
                f'Сравнение описаний {self.__class__} не равносильно сравнению значений элементов. '
                f'Сравнение компонента с собой {self} всегда будет приводить к успешному результату'
            )
            return self.resolved_element is other.resolved_element
        return self.resolved_element is other

    def __eq__(self, other):
        # TODO стоит добавить __ne__, что бы корректно прокинуть not в проверки
        return self._is_equal(other)

    def __bool__(self):
        raise SafetyUsageError(
            f'Взаимодействие осуществляется с описанием элемента {self.__class__}, а не '
            f'с элементом страницы {self}, для проверки свойств используй методы и обращения к свойствам'
        )
