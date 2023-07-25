from ._cookies import get_cookies
from ._headers import get_random_headers
from ._common_config import *


class Getter:
    def __init__(self) -> None:
        self.response = None
        self.manual_cookies = None
    
    def manual_cookies(self, cookies):
        if isinstance(cookies, dict):
            self.manual_cookies = cookies
        if isinstance(cookies, str):
            self.manual_cookies = {i.split("=")[0]:i.split("=")[-1] for i in cookies.split("; ")}
        else:
            raise ValueError("cookies必须为dict或者str类型。")

    def get(self, url, browser_name=None, domain_name='', cookies=None):
        
        self.response = requests.get(url, 
            headers=get_random_headers(), 
            cookies=get_cookies(browser_name=browser_name, domain_name=domain_name) \
                if browser_name is not None else cookies, 
        )

        if int(self.response.status_code) != 200:
            print("status_code:", self.response.status_code)
        
        return self.response.status_code, self.response
    
    def get_soup(self, url, browser_name=None, domain_name='',  cookies=None):
        text = self.get(url, browser_name, domain_name, cookies=cookies)[1].text

        return BeautifulSoup(text, 'html.parser')

    def get_json(self, url, browser_name=None, domain_name='', cookies=None):
        return self.get(url, browser_name, domain_name, cookies=cookies)[1].json()
