import pytest

from web_bricks.utils import checkable


class NewWebBrick:
    def __init__(self, val):
        self.val = val

    @property
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

    def click_assert_seq(self):
        for func in self.val:
            return func()


def seq_gen(seq: list):
    for item in seq:
        print(item)
        yield item


def _assert(assertion):
    def inner_assert():
        raise assertion

    return inner_assert


def _pass(val):
    def inner_pass():
        return val

    return inner_pass


def test_no_extra_params_repr():
    assert repr(checkable(NewWebBrick('str'))) == 'NewWebBrick'


def test_extra_param_repr():
    assert repr(checkable(NewWebBrick('str')).text) == 'NewWebBrick.text'


def test_extra_method_repr():
    assert repr(checkable(NewWebBrick('str')).click()) == 'NewWebBrick.click()'


def test_assert_with_no_extra_params():
    assert bool(checkable(NewWebBrick('str'))) is True


def test_assert_with_no_extra_params_none():
    assert bool(checkable(NewWebBrick(None))) is False


def test_assert_with_no_extra_params_str_bool_true():
    assert bool(checkable(NewWebBrick('True'))) is True


def test_assert_with_no_extra_params_str_bool_false():
    assert bool(checkable(NewWebBrick('False'))) is True


def test_assert_inverted_with_no_extra_params():
    assert bool(not checkable(NewWebBrick('str'))) is False


def test_extra_param_eq():
    assert checkable(NewWebBrick(WebElement('value'))).text == 'value'


def test_extra_param_eq_uneq():
    assert not (checkable(NewWebBrick(WebElement('value'))).text == 'value1')


def test_extra_method_eq():
    assert checkable(NewWebBrick(WebElement('value'))).click() == 'value'


def test_extra_method_apply():
    assert checkable(NewWebBrick(WebElement(
        seq_gen([
            _assert(AssertionError),
            _pass('value')
        ])
    ))).click_assert_seq().apply(swallow=AssertionError) == 'value'


def test_extra_method_apply_attempts():
    assert checkable(NewWebBrick(WebElement(
        seq_gen([
            _assert(AssertionError),
            _assert(AssertionError),
            _assert(AssertionError),
            _pass('value')
        ])
    ))).click_assert_seq().apply(swallow=AssertionError, attempts=4) == 'value'


def test_extra_method_apply_attempts_assert_result():
    with pytest.raises(AssertionError):
        checkable(NewWebBrick(WebElement(
            seq_gen([
                _assert(AssertionError),
                _assert(AssertionError),
                _assert(AssertionError),
                _assert(AssertionError),
                _pass('value')
            ])
        ))).click_assert_seq().apply(swallow=AssertionError, attempts=4)


def test_extra_method_apply_default_attempts_assert_result():
    with pytest.raises(AssertionError):
        checkable(NewWebBrick(WebElement(
            seq_gen([
                _assert(AssertionError),
                _assert(AssertionError),
            ])
        ))).click_assert_seq().apply(swallow=AssertionError)


def test_extra_param_no_eq():
    assert checkable(NewWebBrick(WebElement('value'))).text != 'value1'


def test_extra_param_no_eq__1():
    with pytest.raises(AssertionError) as e:
        assert checkable(NewWebBrick(WebElement('value'))).text == 'value1'
    print(e.value)


def test_extra_param_no_eq_uneq():
    assert not (checkable(NewWebBrick(WebElement('value'))).text != 'value')


def test_extra_param_int_lt():
    assert checkable(NewWebBrick(WebElement(1))).text < 2


def test_extra_param_int_lt_uneq():
    assert not (checkable(NewWebBrick(WebElement(2))).text < 1)


def test_extra_param_int_gt():
    assert checkable(NewWebBrick(WebElement(2))).text > 1


def test_extra_param_int_gt_uneq():
    assert not (checkable(NewWebBrick(WebElement(1))).text > 2)


def test_extra_param_int_le():
    assert checkable(NewWebBrick(WebElement(2))).text <= 2


def test_extra_param_int_le_uneq():
    assert not (checkable(NewWebBrick(WebElement(2))).text <= 1)


def test_extra_param_int_gt_or_eq():
    assert checkable(NewWebBrick(WebElement(1))).text >= 1


def test_extra_param_int_gt_or_eq_uneq():
    assert not (checkable(NewWebBrick(WebElement(1))).text >= 2)
