# 爬取给定影视列表的豆瓣评分和短评

from my_spider import *
from my_spider._common_config import *

import warnings
warnings.filterwarnings('ignore')


FILE_PATH = Path(__file__)
CONFIG_PATH = Path.joinpath(FILE_PATH, 'config.json')


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
    time.sleep(10)
    return driver


def load_dataset(fp, encoding='utf-8'):
    try:
        return pd.read_csv(fp, sep=',', encoding=encoding)
    except:
        return 


def crawler(
    drama_list, 
    vod_type=None,
    page_limit=9, # 刮削页数
    maximize=True, # 最大化浏览器窗口
    open_on_top_screen=True,  # 是否在第二屏幕打开
    storage=True, # 是否需要存储到文件
    fpath='rating.csv',  # 存储路径
    warm_up=False, # 是否追加到文件最后
    use_manager=True, # 是否使用浏览器driver管理器
    page_load_strategy='eager', # driver加载网页策略
    new_window_each_session=False,  # 是否每个会话都新开一个浏览器窗口
    headless=True,  # 是否进入后台运行
    login=False,  # 是否需要登录
    browser_name='Chrome' # 使用浏览器驱动名， 枚举值: Chrome、Edge 
):
    """主程序"""
    douban_url = 'https://movie.douban.com/'

    if vod_type is not None:
        assert isinstance(vod_type, (list, tuple))
        assert len(drama_list) == len(vod_type)

    if warm_up and storage:
        dataset = load_dataset(fpath) 
        if dataset is None:
            dataset = pd.DataFrame(columns=['create_time', 'given_drama_name', 'douban_drama_name', 'rating', 
                                            'short_comment', 'creator', 'stars', 'watch_status', 'stars_comment'])
    else:
        dataset = pd.DataFrame(columns=['create_time', 'given_drama_name', 'douban_drama_name', 'rating', 
                                        'short_comment', 'creator', 'stars', 'watch_status', 'stars_comment'])
    
    def getinto(to_login=login):
        driver = get_driver(browser_name, page_load_strategy=page_load_strategy, use_manager=use_manager, headless=headless)
        if maximize:
            driver = maximize_window(driver, open_on_top_screen=open_on_top_screen)
        driver.get(douban_url)
        if to_login:
            login(driver)
        return driver

    if not new_window_each_session:
        driver = getinto()

    if vod_type is not None:
        iter_list = [(i, j) for i, j in zip(drama_list, vod_type)]
    else:
        iter_list = [(i, None) for i in drama_list]

    for d, vd in tqdm(iter_list):
        d = d.strip()
        
        if d in dataset['given_drama_name'].values:
            continue

        if new_window_each_session:
            driver = getinto(False)

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
                    try:
                        condition = (d in [i.strip() for i in de_text.split(' ')] or d in [i.strip() for i in df_text.split(' / ')]) \
                            and re.search('大陆|香港|台湾', df_text)
                        
                        _test = de_parent.find_elements(By.XPATH, f".//span[@class='label']")[0]
                        if re.findall('\[(.*?)\]', _test.text)[0] == vd:
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

                    de.click() # 点击进入详情页

                    # 点击进入讨论区
                    wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path=f"//h2/i[contains(text(), '短评')]/following-sibling::span[@class='pl']/a[contains(text(), '全部')]",
                        click=True
                    )

                    # 获取当前所有看过，在看，想看
                    is_watched = wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path=f"//li[@class='is-active']/span",
                        index='all'
                    )
                    is_watched.extend(
                            wait_for_show_up(
                            driver, by_method=By.XPATH, 
                            page_path=f"//a[@href='?status=N']",
                            index='all'
                        )
                    )
                    
                    is_watched.extend(
                            wait_for_show_up(
                            driver, by_method=By.XPATH, 
                            page_path=f"//a[@href='?status=F']",
                            index='all'
                        )
                    )

                    ignore_first_element = False

                    iw_page_path = {
                        '看过':"//li[@class='is-active']/span",
                        '在看':"//a[@href='?status=N']",
                        '想看':"//a[@href='?status=F']"
                    }
                    for iw_name, iw_path in iw_page_path.items():
                        iw_element = wait_for_show_up(
                                driver, by_method=By.XPATH, 
                                page_path=iw_path,
                                index=0
                            )
                        if ignore_first_element:
                            if iw_element == None:
                                continue

                            iw_element.click()

                        ignore_first_element = True

                        page_cnt = 0
                        if page_limit is False:
                            page_jump_condition = lambda pc, pl: True
                        else:
                            page_jump_condition = lambda pc, pl: pc < pl

                        while page_jump_condition(page_cnt, page_limit):
                            time.sleep(np.random.randint(1, 4)) # 随机休眠
                            # 获取短评
                            current_elements = wait_for_show_up(
                                                    driver, by_method=By.XPATH, 
                                                    page_path=f"//span[@class='short']",
                                                    index='all'
                                                )
                            
                            if current_elements == [None]:
                                break
                            
                            # 获取所有打星数和地址、发表时间、评论人昵称
                            comment_infoes = wait_for_show_up(
                                        driver, by_method=By.XPATH, 
                                        page_path=f"//span[@class='comment-info']",
                                        index='all'
                            )
                            
                            create_time = []
                            userid = []
                            stars = []
                            stars_comment = []
                            locations = []
                            watch_status = []
                            comments = []

                            for info_e, short_comment in zip(comment_infoes, current_elements):
                                # 获取评论人和发表时间、是否看过
                                creator = info_e.find_element(By.XPATH, f"./a").text
                                ct = info_e.find_element(By.XPATH, f".//span[@class='comment-time ']").text
                                ct = ct.strip()
                                userid.append(creator), create_time.append(ct)

                                watch_status.append(iw_name)

                                try:
                                    ss = info_e.find_element(By.XPATH, f".//span[contains(@class, 'allstar')]")
                                    star = ss.get_attribute("class")
                                    star_comment = ss.get_attribute("title")
                                    star = int(re.findall('allstar(.*?) rating', star)[0]) // 10
                                    stars_comment.append(star_comment), stars.append(star)
                                except:
                                    stars_comment.append('未打星'), stars.append(0) # 未打星

                                # 获取地址
                                try:
                                    address = info_e.find_element(By.XPATH, f".//span[contains(@class, 'comment-location')]")
                                    address = address.text
                                    locations.append(address)
                                except:
                                    address.append('未知')
                                
                                # 获取短评
                                comments.append(short_comment.text)


                            new_ds = pd.DataFrame(data={
                                'create_time':create_time, 'given_drama_name':[d for i in create_time], 'douban_drama_name':[de_text for i in create_time], 
                                'rating':[rating for i in create_time], 'short_comment':comments, 'creator':userid, 'stars':stars, 
                                'watch_status':watch_status, 'stars_comment':stars_comment})
                            
                            dataset = pd.concat((dataset, new_ds), ignore_index=True)

                            # 点击后页
                            if wait_for_show_up(
                                    driver, by_method=By.XPATH, 
                                    page_path=f"//a[@class='next' and text()='后页 >']",
                                    click=True, duration=1
                            ) is not None:
                                page_cnt += 1
                            else:
                                break
                        
                        if page_cnt == 0 and iw_name == '看过':
                            new_ds = pd.DataFrame(data={
                                'create_time':None, 'given_drama_name':d, 'douban_drama_name':de_text, 
                                'rating':rating, 'short_comment':'', 'creator':'', 'stars':'', 'watch_status':'', 'stars_comment':'未打星'}, index=[0])
                            
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
    # drama_list = ['美丽战场', '大侠霍元甲', '射雕英雄传', '神雕侠侣']
    drama_list = ['美丽战场']
    page_limit = False # 目前豆瓣限制游客只能看前十页短评

    print(crawler(drama_list, vod_type=['剧集'], page_limit=page_limit, storage=True, use_manager=True, headless=False))  # 不需要存储进硬盘
