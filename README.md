# Web-Bricks

## Install

```bash
python3 -m pip install web-bricks
```

## Usage

Example page:
```html
<html>
  <body>
    <div data-n="single-element-on-root-page">
    <div data-n="block-on-root-page">
      <ul>
        <li data-n="element-of-list">Cheburechka</li>
        <li data-n="element-of-list">Some value</li>
        <li data-n="element-of-list">Some Another Value</li>
     </ul>
  </body>
</html>
```


### WebBrick

#### Make Driver Actions
```python
# PlayWright
from web_bricks import WebBrick
from playwright.async_api import ElementHandle


class WebElement(WebBrick):
    async def element(self) -> ElementHandle:
        return await self.driver.wait_for_selector(f'xpath={self.full_locator_str}')
    
    async def tap(self):
        return await self.element.tap()
    
    async def is_visible(self):
        try:
            await self.driver.wait_for_selector(f'xpath={self.full_locator_str}', state='visible')
        except TimeoutError as e:
            return False
        return True
    
    @property
    async def inner_text(self):
        return await self.element.inner_text('value')

```
#### Make Page Object Tree Interface
```python
from web_bricks import many
from typing import List

class RootPageSingleElement(WebElement):
    LOCATOR = '//*[@data-n="single-element-on-root-page"]'

class RootPageListElements(WebElement):
    LOCATOR = '//*[@data-n="element-of-list"]'
    
class RootPageBlock(WebElement):
    LOCATOR = '//*[@data-n="block-on-root-page"]'
    
    @property
    def element_of_list(self) -> List[RootPageListElements]:
        return many(RootPageListElements(self))   
    
class RootPage(WebElement):
    LOCATOR = '/*'
    
    @property
    def single_element(self) -> RootPageSingleElement:
        return RootPageSingleElement(self)   
    
    @property
    def block(self) -> RootPageBlock:
        return RootPageBlock(self)
```
#### Do the things
```python
from web_brick import str_xpath_locator_extractor

with async_playwright() as playwright:
    browser = playwright.chromium.lunch()
    page = browser.new_page() 
    
    # treat LOCATOR as xpath string
    app = RootPage(page, config=WebBricksConfig(locator_repr_extractor=xpath_str_locator_extractor)
    
    # Interact with PO
    var_zero_elem_value = await app.block.element_of_list[0].inner_text
    
    await app.single_element.tap()
    assert await app.block.is_visible()
    assert app.block.element_of_list[0].is_visible()
    
    assert app.block.element_of_list[0].inner_text == 'SomeValue'
    assert app.block.element_of_list[3].inner_text == var_zero_elem_value
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
