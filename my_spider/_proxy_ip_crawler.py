# 免费代理ip爬虫

from ._common_config import *
from ._url_ops import *


class ProxyFetcher:
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        try:
            start_url = "https://www.zdaye.com/dayProxy.html"
            html_tree = Getter().get(start_url, verify=False).tree
            latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
            interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
            if interval.seconds < 300:  # 只采集5分钟内的更新
                target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
                while target_url:
                    _tree = Getter().get(target_url, verify=False).tree
                    for tr in _tree.xpath("//table//tr"):
                        ip = "".join(tr.xpath("./td[1]/text()")).strip()
                        port = "".join(tr.xpath("./td[2]/text()")).strip()
                        yield "%s:%s" % (ip, port)
                    next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                    target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                    time.sleep(5)
        except:
            yield None

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = Getter().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = Getter().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy04(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = Getter().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            time.sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy05():
        """ FateZero http://proxylist.fatezero.org/ """
        url = "http://proxylist.fatezero.org/proxy.list"
        try:
            resp_text = Getter().get(url).text
            for each in resp_text.split("\n"):
                json_info = json.loads(each)
                if json_info.get("country") == "CN":
                    yield "%s:%s" % (json_info.get("host", ""), json_info.get("port", ""))
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy06():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = Getter().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy07():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = Getter().get(url, timeout=20)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 89免费代理 """
        r = Getter().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy09():
        """ 稻壳代理 https://www.docip.net/ """
        r = Getter().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)


@lru_cache(maxsize=None)
def cache_ip(date):
    """每天更新一次"""
    ip_list = []

    pf = ProxyFetcher()

    pf_funcs = [
        pf.freeProxy01, pf.freeProxy02, pf.freeProxy03, pf.freeProxy04,
        pf.freeProxy05, pf.freeProxy06, pf.freeProxy07, pf.freeProxy08,
        pf.freeProxy09
    ]

    for func in tqdm(pf_funcs, desc="fetching proxy ip"):
        for i in func():
            ip_list.append(i)

    ip_list = list(set(ip_list))

    return ip_list


def get_proxy_ip(invalid_ip):
    """获取每次获取一个ip:port"""
    assert isinstance(invalid_ip, list)

    date = datetime.now().date().strftime('%Y%m%d')

    ips = cache_ip(date)

    to_choice_list = list(set(ips) - set(invalid_ip))
    while len(to_choice_list) > 0:
        return random.choice(to_choice_list)
