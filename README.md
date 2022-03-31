# web-bricks

## install

```bash
python3 -m pip install git@github.com:2gis-test-labs/web-bricks.git
```

or

```bash 
cat 'git@github.com:2gis-test-labs/web-bricks.git@v0.0.3#egg=web-bricks' >> requirements.txt
```

## Usage

```python
from web_bricks import WebBricksConfig, web_resolver, WebBrick, many
from typing import List

# at PageObject:

# просто какая то функция композиции локаторов
def make_locator(val):
    return {'by': 'css', 'value': val}


class SubElement(WebBrick):
    pass


class MoreSubElement(WebBrick):
    pass


class RootPage(WebBrick):
    @property
    def sub_page(self) -> SubElement:
        locator = make_locator('some')
        return SubElement(self, locator)

    @property
    def sub_elements(self) -> List[MoreSubElement]:
        return many(MoreSubElement(self, locator=make_locator('another')))


# at TearUp:

selenium_resolver_config = WebBricksConfig(
    resolver=web_resolver(waiter=SeleniumWaiter, timeout=10)
)
selenium_driver = webdriver.Remote(...)
root_page = RootPage(selenium_driver, locator=make_locator(':root'), config=selenium_resolver_config)

# at Test:
root_page.sub_page.resolved_element.click()
root_page.sub_elements[1].resolved_element.click()
root_page.sub_elements[1].resolved_element.text
```

## Прогнать тесты

```bash
python3 -m pip install -r requiremnts.txt
python3 -m pip install -r requiremnts-dev.txt
pytest tests
```

## Установить библиотеку локально-
```bash
python3 -m pip install .
```
