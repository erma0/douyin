import pytest

from lib.cookies import get_cookie_dict, get_browser_cookie

ck_text = "store-region=cn-sh; store-region-src=uid;"


@pytest.mark.parametrize('browser', [ck_text, ''])
def test_cookie_dict(browser):
    assert get_cookie_dict(browser)


@pytest.mark.parametrize('browser', ['edge', 'chrome', 'load'])
def test_browser_cookie(browser):
    assert get_browser_cookie(browser)
