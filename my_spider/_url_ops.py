from ._cookies import get_cookies
from ._headers import get_random_headers
from ._common_config import *


class BaseOps:
    def __init__(self) -> None:
        self.response = None
        self.manual_cookies = None
        self.status_code = None
    
    def manual_cookies(self, cookies):
        if isinstance(cookies, dict):
            self.manual_cookies = cookies
        if isinstance(cookies, str):
            self.manual_cookies = {i.split("=")[0]:i.split("=")[-1] for i in cookies.split("; ")}
        else:
            raise ValueError("cookies必须为dict或者str类型。")


class Getter(BaseOps):
    def get(self, url, browser_name=None, domain_name='', cookies=None, **request_kwargs):
        self.response = requests.get(url, 
            headers=get_random_headers(), 
            cookies=get_cookies(browser_name=browser_name, domain_name=domain_name) \
                if browser_name is not None else cookies, 
            **request_kwargs
        )

        if int(self.response.status_code) != 200:
            print("status_code:", self.response.status_code)
        
        self.status_code = self.response.status_code
        
        return self
    
    @property
    def soup(self):
        text = self.response.text

        return BeautifulSoup(text, 'html.parser')

    @property
    def json(self):
        return self.response.json()
    
    @property
    def tree(self):
        return etree.HTML(self.response.content)
    
    @property
    def text(self):
        return self.response.text
