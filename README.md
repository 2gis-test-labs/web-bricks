# Web-Bricks

## Install

```bash
python3 -m pip install web-bricks
```

## Usage

```python
from web_bricks import WebBricksConfig, web_resolver, WebBrick, many, checkable
from typing import List


# at PageObject:

# просто какая то функция композиции локаторов
def make_locator(val):
    return {'by': 'css', 'value': val}


class WebElement(WebBrick):
    def click(self):
        return checkable(self).click().apply()
    
    def get_text(self):
        return checkable(self).text  # driver method
    
    def text(self):
        return self.get_text().apply()


class SubElement(WebElement):
    pass


class MoreSubElement(WebElement):
    pass


class RootPage(WebElement):
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

# Development

## Tests

```bash
make test-all
```

## Local dev
```bash
make dev-install
```
