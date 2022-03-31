import pytest
from jj import Response
from mocked_response import MockedResponse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from web_bricks import WebBrick, WebBricksConfig, web_resolver

app_mock_url = "http://test-app:80/"
mocked_response = MockedResponse(app_mock_url)

selenium_chrome_url = "http://chrome:4444/wd/hub"

resolver = web_resolver(
    WebDriverWait,
    ignored_exceptions=(NoSuchElementException, TimeoutException),
    timeout=1
)

config = WebBricksConfig(
    resolver=resolver,
)


@pytest.fixture
def selenium():
    driver = webdriver.Remote(command_executor=selenium_chrome_url, desired_capabilities=DesiredCapabilities.CHROME)
    yield driver
    driver.close()


def make_css_locator(value):
    return {'by': By.CSS_SELECTOR, 'value': value}


def test_empty_selenium_interaction(selenium):
    body = '''<html><head></head><body></body></html>'''
    header = {'Content-Type': 'text/html; charset=utf-8'}

    class RootPage(WebBrick):
        pass

    page_object_tree = RootPage(selenium, locator=make_css_locator(':root'), config=config)

    with mocked_response('GET', "/", response=Response(body=body, headers=header)):
        selenium.get(app_mock_url)
        page_res = page_object_tree.resolved_element.get_attribute('innerHTML')

    assert f'<html>{page_res}</html>' == body


def test_simple_selenium_interaction(selenium):
    element_text = 'element1'
    element_id = 'element1'
    body = f'<html><head></head><body><div id="element0">element0</div>' \
           f'<div id="{element_id}">{element_text}</div></body></html>'
    header = {'Content-Type': 'text/html; charset=utf-8'}

    class SubElement(WebBrick):
        locator = make_css_locator(f'#{element_id}')

    class RootPage(WebBrick):
        @property
        def sub_element(self):
            return SubElement(self, SubElement.locator)

    page_object_tree = RootPage(selenium, locator=make_css_locator(':root'), config=config)

    with mocked_response('GET', "/", response=Response(body=body, headers=header)):
        selenium.get(app_mock_url)
        text_res = page_object_tree.sub_element.resolved_element.text

    assert text_res == element_text
