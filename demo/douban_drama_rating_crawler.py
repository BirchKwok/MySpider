# 爬取给定影视列表的豆瓣评分信息

from my_spider import *
from my_spider._common_config import *

import warnings
warnings.filterwarnings('ignore')


FILE_PATH = Path(__file__)
CONFIG_PATH = Path.joinpath(FILE_PATH.parent, 'config.json')


def maximize_window(driver, maximize=True, open_on_top_screen=True):
    if open_on_top_screen:
        driver.set_window_position(0, -1000)
    
    if maximize:
        driver.maximize_window()

    return driver


def json_load(fp):
    with open(fp, 'r', encoding='utf8') as f:
        return json.load(f)


def login(driver, account_id=None, passwd=None):
    # 点击顶栏
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//div[@class="top-nav-info"]/a[@class="nav-login"]',
        click=True
    )

    # 点击密码登录
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//li[@class="account-tab-account" and text()="密码登录"]',
        click=True
    )

    # 填入账号
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//input[@id="username" and @class="account-form-input" and @placeholder="手机号 / 邮箱" and @tabindex="1"]',
        click=True,
        send_keys=json_load(CONFIG_PATH)['douban_account'] if account_id is None else account_id
    )

    # 填入密码
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//input[@id="password" and @class="account-form-input password" and @placeholder="密码" and @tabindex="3"]',
        click=True,
        send_keys=json_load(CONFIG_PATH)['douban_passwd'] if passwd is None else passwd
    )

    # 点击登录
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//a[@class="btn btn-account btn-active" and text()="登录豆瓣"]',
        click=True
    )

    # 休眠10秒钟等待手动验证
    time.sleep(40)
    return driver


def load_dataset(fp, encoding='utf-8'):
    try:
        return pd.read_csv(fp, sep=',', encoding=encoding)
    except:
        return 


def crawler(
    drama_list, 
    vod_type=None,
    release_year=None,
    maximize=True, # 最大化浏览器窗口
    open_on_top_screen=True,  # 是否在第二屏幕打开
    storage=True, # 是否需要存储到文件
    fpath='rating.csv',  # 存储路径
    warm_up=False, # 是否追加到文件最后
    use_manager=True, # 是否使用浏览器driver管理器
    page_load_strategy='eager', # driver加载网页策略
    new_window_each_session=False,  # 是否每个会话都新开一个浏览器窗口
    headless=True,  # 是否进入后台运行
    to_login=False,  # 是否需要登录
    browser_name='Chrome', # 使用浏览器驱动名， 枚举值: Chrome、Edge 
    ip=None  # 代理ip和端口  形如 xxx.xxx.xxx.xxx:xxx
):
    """主程序"""
    douban_url = 'https://movie.douban.com/'

    if vod_type is not None:
        assert isinstance(vod_type, (list, tuple))
        assert len(drama_list) == len(vod_type)
    
    if release_year is not None:
        assert len(drama_list) == len(release_year)

    if warm_up and storage:
        dataset = load_dataset(fpath) 
        if dataset is None:
            dataset = pd.DataFrame(columns=['given_drama_name', 'douban_drama_name', 'rating', 'comments_num', 'pointed_num'])
    else:
        dataset = pd.DataFrame(columns=['given_drama_name', 'douban_drama_name', 'rating', 'comments_num', 'pointed_num'])
    
    def getinto(to_login=to_login):
        driver = get_driver(browser_name, page_load_strategy=page_load_strategy, use_manager=use_manager, headless=headless, ip=ip)
        if maximize:
            driver = maximize_window(driver, open_on_top_screen=open_on_top_screen)
        driver.get(douban_url)
        if to_login:
            login(driver)
        return driver

    if not new_window_each_session:
        driver = getinto(to_login)

    if vod_type is not None and release_year is None:
        iter_list = [(i, j, None) for i, j in zip(drama_list, vod_type)]
    elif vod_type is not None and release_year is not None:
        iter_list = [(i, j, k) for i, j, k in zip(drama_list, vod_type, release_year)]
    elif vod_type is None and release_year is not None:
        iter_list = [(i, None, k) for i, k in zip(drama_list, release_year)]
    else:
        iter_list = [(i, None, None) for i in drama_list]

    for d, vd, ry in tqdm(iter_list):
        d = d.strip()
        
        if d in dataset['given_drama_name'].values:
            continue

        if new_window_each_session:
            driver = getinto(to_login)

        # 输入搜索框
        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
            send_keys=d
        )

        # 点击搜索
        wait_for_show_up(
                driver, by_method=By.XPATH, 
                page_path="//input[@type='submit' and @value='搜索']", 
                click=True
        )

        # 找到所有搜索结果
        drama_es = wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    # 找到和给定剧集匹配的标签
                    page_path=f"//div[@class='detail']/div[@class='title']", index='all'
            )
        
        drama_name = wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    # 找到和给定剧集匹配的标签
                    page_path=f"//a[@class='title-text']", index='all'
            )
        
        dramas_from = wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    # 首选是中国的剧集
                    page_path=f"//div[@class='meta abstract']", 
                    index='all'
            )
        
        if drama_es != [None] and dramas_from != [None]:
            for (de_parent, df, de) in zip(drama_es, dramas_from, drama_name):

                de_text = de.text
                df_text = df.text
                
                if vod_type is None:
                    condition = (d in [i.strip() for i in de_text.split(' ')] or d in [i.strip() for i in df_text.split(' / ')]) \
                            and re.search('大陆|香港|台湾', df_text)
                else:
                    if release_year is None:
                        try:
                            condition = (d in [i.strip() for i in de_text.split(' ')] or d in [i.strip() for i in df_text.split(' / ')]) \
                                and re.search('大陆|香港|台湾', df_text)
                            
                            _test = de_parent.find_elements(By.XPATH, f".//span[@class='label']")[0]
                            if re.findall('\[(.*?)\]', _test.text)[0] == vd:
                                condition = True and condition
                        except:
                            condition = False
                    else:
                        try:
                            condition = (d in [i.strip() for i in de_text.split(' ')] or d in [i.strip() for i in df_text.split(' / ')]) \
                                and re.search('大陆|香港|台湾', df_text)
                            
                            _test = de_parent.find_elements(By.XPATH, f".//span[@class='label']")[0]
                            if re.findall('\[(.*?)\]', _test.text)[0] == vd:
                                condition = True and condition

                            if int(re.findall(' \((.*?)\)', de_text)[0]) == int(ry):
                                condition = True and condition
                        except:
                            condition = False

                if condition:
                    # 获取评分
                    rate_element = wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path="//span[@class='rating_nums']", 
                    )

                    try:
                        rating = rate_element.text  # 总体评分
                    except:
                        rating = None
                    
                    pointed_num = wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path="//span[@class='pl']", 
                    ).text

                    try:
                        if pointed_num != '(暂无评分)':
                            pointed_num = int(re.findall('\((.*?)人评价\)', pointed_num)[0].strip())
                        else:
                            pointed_num = 0
                    except:
                        pointed_num = 0

                    de.click() # 点击进入详情页

                    # 获取多少条短评
                    comments_num = wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path=f"//h2/i[contains(text(), '短评')]/following-sibling::span[@class='pl']/a[contains(text(), '全部')]",
                    ).text

                    try:
                        if comments_num != '全部 0 条':
                            comments_num = int(re.findall('全部 (.*?) 条', comments_num)[0].strip())
                        else:
                            comments_num = 0
                    except:
                        comments_num = 0

                    new_ds = pd.DataFrame(data={
                        'given_drama_name':d, 'douban_drama_name':de_text, 
                        'rating':rating, 'comments_num':comments_num, 'pointed_num':pointed_num}, index=[0])
                    
                    dataset = pd.concat((dataset, new_ds), ignore_index=True)
                    
                    break # 跳出搜索列表循环

            if storage:
                dataset.to_csv(fpath, sep=',', encoding='utf-8', index=False)

        if new_window_each_session:
            driver.quit()
        else:
            wait_for_show_up(
                driver, by_method=By.XPATH, 
                page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
            ).clear() # 清空搜索框

    if not new_window_each_session:
        driver.quit()

    return dataset


if __name__ == '__main__':
    invalid_ip = []

    # drama_list = ['美丽战场', '大侠霍元甲', '射雕英雄传', '神雕侠侣']
    # drama_list = ['美丽战场']
    # page_limit = 1 # 目前豆瓣限制游客只能看前十页短评

    drama_list = pd.read_csv('~/drama_names.csv')['episode_cn'].values
    # drama_release_year = pd.read_csv('~/drama_names.csv')['first_play_date'].values

    # ip = get_proxy_ip(invalid_ip=invalid_ip, proxy_type='https')

    dataset = crawler(drama_list, vod_type=['剧集'] * len(drama_list), release_year=None, storage=True, warm_up=True,
                                  use_manager=False, headless=True, browser_name='Chrome', to_login=False, ip=None)

    # while True:
    #     ip = get_proxy_ip(invalid_ip=invalid_ip, proxy_type='https')
    #     if ip:
    #         print("current ip: ", ip)
    #         try:
    #             dataset = crawler(drama_list, vod_type=['剧集'], page_limit=page_limit, storage=False, 
    #                               use_manager=False, headless=False, browser_name='Chrome',ip=ip, to_login=True)
    #             break
    #         except:
    #             print('invalid.')

    #             invalid_ip.append(ip)
    #             continue
    #     else:
    #         break
    
    print(dataset)

