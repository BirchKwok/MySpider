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
        小舒代理 https://www.xsdaili.cn/
        """
        try:
            start_url = "https://www.xsdaili.cn/"
            html_tree = Requester().get(start_url, verify=False).tree

            content_titles = html_tree.xpath("//div[@class='table table-hover panel-default panel ips ']/div[@class='title']/a/text()")
            for title in content_titles:
                latest_page_time = title.split(' ')[0].strip()

                interval = datetime.now() - datetime.strptime(latest_page_time, "%Y年%m月%d日")
                if interval.days < 14:  # 只采集2周内的更新
                    target_url = "https://www.xsdaili.cn/" + html_tree.xpath("//div[@class='table table-hover panel-default panel ips ']/div[@class='title']/a/@href")[0].strip()
    
                    _tree = Requester().get(target_url, verify=False).tree
                    for line in _tree.xpath("//div[@class='cont']/text()"):
                        text = line.split('@')[0].strip()
                        if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}', text):
                            yield text
        except:
            yield None

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        try:
            url = "http://www.66ip.cn/{}.html"
            for page in range(1, 20):  # 采集前20页
                subpage_url = url.format(page)
                resp = Requester().get(subpage_url, timeout=10, verify=False).tree
                for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
                    if i > 0:
                        ip = "".join(tr.xpath("./td[1]/text()")).strip()
                        port = "".join(tr.xpath("./td[2]/text()")).strip()
                        yield "%s:%s" % (ip, port)
        except:
            yield None

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = Requester().get(url).tree
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
        for page_index in range(1, page_count + 3): # 爬3页
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = Requester().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            time.sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy05():
        """ FateZero http://proxylist.fatezero.org/ """
        url = "http://proxylist.fatezero.org/proxy.list"
        try:
            resp_text = Requester().get(url).text
            for each in resp_text.split("\n"):
                json_info = json.loads(each)
                if json_info.get("country") == "CN":
                    yield "%s:%s" % (json_info.get("host", ""), json_info.get("port", ""))
        except Exception as e:
            pass

    @staticmethod
    def freeProxy06():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = Requester().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy07():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = Requester().get(url, timeout=20)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 89免费代理 """
        r = Requester().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy09():
        """ 稻壳代理 https://www.docip.net/ """
        r = Requester().get("https://www.docip.net/data/free.json", verify=False)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            pass


async def https_ip_detect(proxy):
    """异步检测代理是否支持https"""
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get('https://www.baidu.com', proxy='http://'+proxy, timeout=10) as response:
                if response.status == 200:
                    await response.text()
        
                    return proxy
                else:
                    return
        except:
            return
    

def memoize(fn):
    cache = {}
    miss = object()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = cache.get(args, miss)
        if result is miss:
            result = fn(*args, **kwargs)
            cache[args] = result
        return result

    def clear_cache():
        cache.clear()

    wrapper.clear_cache = clear_cache
    return wrapper


@memoize
def cache_ip(hour, proxy_type=None):
    """每小时更新一次"""

    if isinstance(proxy_type, str):
        proxy_type = proxy_type.upper()

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

    if proxy_type == 'HTTPS':
        tasks = [
            asyncio.ensure_future(https_ip_detect(i))
            for i in ip_list
        ]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

        ip_list = [i.result() for i in tasks]

        res = []
        for i in ip_list:
            if i is None:
                continue
            if isinstance(i, Sized) and not isinstance(i, str):
                res.extend(i)
            elif i != '':
                res.append(i)
            
        ip_list = res

    return np.unique(ip_list).tolist()


def get_proxy_ip(invalid_ip, proxy_type=None, include_local_ip=True):
    """获取每次获取一个ip:port， 逐小时更新"""
    assert isinstance(invalid_ip, list)

    hour = datetime.now().strftime('%Y%m%d%H')

    ips = cache_ip(hour, proxy_type=proxy_type)

    if include_local_ip:
        ips = [*ips, '127.0.0.1:8888']

    to_choice_list = list(set(ips) - set(invalid_ip))
    print(f"{len(to_choice_list)} ip addresses are available in the ip-pool.")
    
    if len(to_choice_list) > 0:
        return random.choice(to_choice_list)
    