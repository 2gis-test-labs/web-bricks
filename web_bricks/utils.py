from typing import Any, Callable, List, TypeVar, Union

from rtry import retry

from .component import WebBrick

T = TypeVar('T', bound=Union[None, WebBrick])


def many(web_brick: T) -> List[T]:
    return web_brick.list()


class PromisedBrick:
    def __init__(self, brick, attr=None, call=None, check=None, attempts=None, timeout=None):
        self._brick = brick
        self.custom_attr = attr
        self.call = call
        self.check = check
        self.attempts = attempts or 3
        self.timeout = timeout or 1
        self.res = ''

    def __getattr__(self, item):
        if item in ['custom_attr', 'call', 'check', 'apply', 'res']:
            return object.__getattribute__(self, item)
        return PromisedBrick(self, attr=item, call=None, check=None, attempts=self.attempts, timeout=self.timeout)

    def __call__(self, *args, **kwargs):
        return PromisedBrick(self, attr=None, call=(args, kwargs), check=None, attempts=self.attempts,
                             timeout=self.timeout)

    def __eq__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('==', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __ne__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('!=', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __lt__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('<', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __gt__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('>', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __le__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('<=', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __ge__(self, other):
        return PromisedBrick(self, attr=None, call=None, check=('>=', other), attempts=self.attempts,
                             timeout=self.timeout)

    def __repr__(self):
        attr_name = ''
        if self.__getattribute__('custom_attr'):
            attr = self.__getattribute__('custom_attr')
            attr_name = ('.' + attr) if attr else ''

        params = ''
        if self.__getattribute__('call'):
            call_attr = self.__getattribute__('call')
            args, kwargs = call_attr
            args = [str(item) for item in args]
            kwargs = [f'{k}={v}' for k, v in kwargs.items()]
            params = '({})'.format(', '.join(args + kwargs)) if (args + kwargs) else '()'

        check_type = ''
        if self.__getattribute__('check'):
            check_type = ' ' + self.__getattribute__('check')[0]

        check_value = ''
        if self.__getattribute__('check'):
            check_value = ' ' + self.__getattribute__('check')[1]

        res = ''
        if self.__getattribute__('res'):
            # res добавляется только при разрешении PromizedBrick и самого WebBrick
            res = ' = ' + self.__getattribute__('res')
        a = f"{self._brick}" \
            f"{attr_name}" \
            f"{params}" \
            f"{res}" \
            f"{check_type}" \
            f"{check_value}"
        return a

    def resolved_element(self):
        subj = self._brick

        if hasattr(subj, 'resolved_element'):
            if isinstance(subj.resolved_element, Callable):
                subj = subj.resolved_element()
            else:
                subj = subj.resolved_element

        if self.__getattribute__('custom_attr'):
            subj = object.__getattribute__(subj, self.custom_attr)

        if self.__getattribute__('call'):
            args, kwargs = self.__getattribute__('call')
            subj = subj(*args, **kwargs)

        self.__setattr__('res', f'{subj}')
        if self.__getattribute__('check'):
            op = self.__getattribute__('check')[0]
            other = self.__getattribute__('check')[1]
            # Что бы сохранить приоритеты для rvalue приоритетных операций над other
            if op == '==':
                return subj == other
            elif op == '!=':
                return subj != other
            elif op == '>':
                return subj > other
            elif op == '<':
                return subj < other
            elif op == '>=':
                return subj >= other
            elif op == '<=':
                return subj <= other
        return subj

    def __bool__(self):
        return retry(until=lambda x: x is True, attempts=3, timeout=1)(lambda: bool(self.resolved_element()))()

    def apply(self, swallow, attempts=2, delay=0, timeout=100):
        return retry(
            swallow=swallow, attempts=attempts, delay=delay, timeout=timeout
        )(
            lambda: self.resolved_element()
        )()


R = TypeVar('R', bound=Union[None, WebBrick, Any])


def checkable(web_brick: {R}) -> R:  # type: ignore
    return PromisedBrick(web_brick)  # type: ignore
