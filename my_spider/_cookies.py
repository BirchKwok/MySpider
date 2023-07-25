# 当前所有可用浏览器名称
available_browsers = [
    "Chrome", "Firefox", "Opera", "Edge", "Chromium", "Brave", "Vivaldi", 
    "Safari"
]


def get_cookies(browser_name=None, domain_name=''):
    """
    获取特定浏览器 cookies

    browser_name: str, can be Chrome/Firefox/Opera/Edge/Chromium/Brave/Vivaldi/Safari
    """
    assert browser_name in [
        None, *available_browsers
    ]

    import browser_cookie3
    browsers = {
            "Chrome": browser_cookie3.chrome,
            "Firefox": browser_cookie3.firefox,
            "Opera": browser_cookie3.opera,
            "Edge": browser_cookie3.edge,
            "Chromium": browser_cookie3.chromium,
            "Brave": browser_cookie3.brave,
            "Vivaldi": browser_cookie3.vivaldi,
            "Safari": browser_cookie3.safari
        }

    return browsers[browser_name](domain_name=domain_name) if browser_name is not None else None
