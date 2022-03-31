from d42 import schema

from web_bricks.utils import checkable


class NewWebBrick:
    def __init__(self, val):
        self.val = val

    def resolved_element(self):
        return self.val

    def __repr__(self):
        return 'NewWebBrick'


class WebElement:
    def __init__(self, val):
        self.val = val

    @property
    def text(self):
        return self.val

    def click(self):
        return self.val


def test_extra_param_eq():
    assert checkable(NewWebBrick(WebElement('value'))).text == schema.str('value')


def test_extra_param_eq_uneq0():
    assert not (checkable(NewWebBrick(WebElement('value'))).text == schema.str('value1'))


def test_extra_param_eq_uneq1():
    assert checkable(NewWebBrick(WebElement('value'))).text != schema.str('value1')


def test_extra_method_eq():
    assert checkable(NewWebBrick(WebElement('value'))).click() == schema.str('value')


def test_extra_param_no_eq():
    assert checkable(NewWebBrick(WebElement('value'))).text != schema.str('value1')


def test_extra_param_no_eq_uneq():
    assert not (checkable(NewWebBrick(WebElement('value'))).text != schema.str('value'))


def test_extra_param_int_lt():
    assert checkable(NewWebBrick(WebElement(1))).text == schema.int.max(1)


def test_extra_param_int_lt_uneq():
    assert not (checkable(NewWebBrick(WebElement(2))).text == schema.int.max(1))


def test_extra_param_int_gt():
    assert checkable(NewWebBrick(WebElement(2))).text == schema.int.min(1)


def test_extra_param_int_gt_uneq():
    assert not (checkable(NewWebBrick(WebElement(1))).text == schema.int.min(2))


def test_extra_param_int_le():
    assert checkable(NewWebBrick(WebElement(2))).text == schema.int.max(2)


def test_extra_param_int_le_uneq():
    assert not (checkable(NewWebBrick(WebElement(2))).text == schema.int.max(1))


def test_extra_param_int_gt_or_eq():
    assert checkable(NewWebBrick(WebElement(1))).text == schema.int.min(1)


def test_extra_param_int_gt_or_eq_uneq():
    assert not (checkable(NewWebBrick(WebElement(1))).text == schema.int.min(2))


def test_empty_string():
    assert checkable(NewWebBrick(WebElement(''))).text == schema.str.len(0)


def test_not_empty_string():
    assert checkable(NewWebBrick(WebElement('asd'))).text == schema.str.len(2, 4)


def test_empty_non_empty():
    assert not (checkable(NewWebBrick(WebElement('asd'))).text == schema.str.len(0))


def test_non_empty_empty():
    assert not (checkable(NewWebBrick(WebElement(''))).text == schema.str.len(2, 4))
