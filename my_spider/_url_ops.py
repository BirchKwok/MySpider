from ._cookies import get_cookies
from ._headers import get_random_headers
from ._common_config import *


class BaseOps:
    def __init__(self, headers_supplement=None) -> None:
        self.response = None
        self.manual_cookies = None
        self.last_status_code = None
        self.headers_supplement = headers_supplement
    
    def manual_cookies(self, cookies):
        if isinstance(cookies, dict):
            self.manual_cookies = cookies
        if isinstance(cookies, str):
            self.manual_cookies = {i.split("=")[0]:i.split("=")[-1] for i in cookies.split("; ")}
        else:
            raise ValueError("cookies必须为dict或者str类型。")
        
    def get_soup(*args, **kwargs):
        raise NotImplementedError
    
    def get_json(*args, **kwargs):
        raise NotImplementedError


class Getter(BaseOps):
    def get(self, url, browser_name=None, domain_name='', cookies=None):
        self.response = requests.get(url, 
            headers=get_random_headers(), 
            cookies=get_cookies(browser_name=browser_name, domain_name=domain_name) \
                if browser_name is not None else cookies, 
        )

        if int(self.response.status_code) != 200:
            print("status_code:", self.response.status_code)
        
        self.last_status_code = self.response.status_code
        
        return self.response.status_code, self.response
    
    def get_soup(self, *args, **kwargs):
        text = self.get(*args, **kwargs)[1].text

        return BeautifulSoup(text, 'html.parser')

    def get_json(self, *args, **kwargs):
        return self.get(*args, **kwargs)[1].json()


class Postter(BaseOps):
    def post(self, url, data, browser_name=None, domain_name='', cookies=None):
        headers=get_random_headers()
        headers['content-type'] = 'application/json'
        self.response = requests.post(
            url, json=data,
            headers=headers, 
            cookies=get_cookies(browser_name=browser_name, domain_name=domain_name) \
                if browser_name is not None else cookies
            )
        
        if int(self.response.status_code) != 200:
            print("status_code:", self.response.status_code)
        
        self.last_status_code = self.response.status_code
        
        return self.response.status_code, self.response

    def get_soup(self, *args, **kwargs):
        text = self.post(*args, **kwargs)[1].text

        return BeautifulSoup(text, 'html.parser')

    def get_json(self, *args, **kwargs):
        return self.post(*args, **kwargs)[1].json()
