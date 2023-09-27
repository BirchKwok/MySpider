# 爬取给定影视列表的豆瓣评分和短评

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
    release_years=None,
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
    to_login=False,  # 是否需要登录
    browser_name='Chrome', # 使用浏览器驱动名， 枚举值: Chrome、Edge 
    ip=None  # 代理ip和端口  形如 xxx.xxx.xxx.xxx:xxx
):
    """主程序"""
    douban_url = 'https://movie.douban.com/'

    if vod_type is not None:
        assert isinstance(vod_type, (list, tuple, dict))
        assert len(drama_list) == len(vod_type)
    
    if release_years is not None:
        # 发行日期
        assert isinstance(release_years, (list, tuple, dict))

    if warm_up and storage:
        dataset = load_dataset(fpath) 
        if dataset is None:
            dataset = pd.DataFrame(columns=['create_time', 'given_drama_name', 'douban_drama_name', 'rating', 
                                            'short_comment', 'creator', 'stars', 'watch_status', 'stars_comment', 'locations', 'watched', 'watching', 'want2watch'
                                            ])
    else:
        dataset = pd.DataFrame(columns=['create_time', 'given_drama_name', 'douban_drama_name', 'rating', 
                                        'short_comment', 'creator', 'stars', 'watch_status', 'stars_comment', 'locations', 'watched', 'watching', 'want2watch'
                                        ])
    
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

    if vod_type is not None:
        iter_list = [(i, j) for i, j in zip(drama_list, vod_type)]
    else:
        iter_list = [(i, None) for i in drama_list]

    for d, vd in tqdm(iter_list):
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

                # 根据条件筛选剧集
                condition = (d in [i.strip() for i in de_text.split(' ')] or d in [i.strip() for i in df_text.split(' / ')]) \
                            and re.search('大陆|香港|台湾', df_text)

                if vod_type is not None:
                    try:                        
                        _test = de_parent.find_elements(By.XPATH, f".//span[@class='label']")[0]
                        if re.findall('\[(.*?)\]', _test.text)[0] == vd:
                            condition = True and condition
                    except:
                        pass
                
                # 年份判断
                if release_years is not None:
                    if isinstance(release_years, (list, tuple)):
                        assert len(release_years) == len(drama_list)

                        condition = condition and int(release_years[drama_list.index(d)]) == int(re.findall('\((.*?)\)', de_text.split(' ')[-1])[0])
                    else:
                        rls_yrs = release_years.get(d)
                        if rls_yrs:
                            condition = condition and (int(rls_yrs) == int(re.findall('\((.*?)\)', de_text.split(' ')[-1])[0]))

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

                    watched, watching, want2watch = 0, 0, 0
                    for iw_name, iw_path in iw_page_path.items():
                        iw_element = wait_for_show_up(
                                driver, by_method=By.XPATH, 
                                page_path=iw_path,
                                index=0
                            )
                        if iw_name == '看过':
                            watched = int(re.split('[\(\)]', iw_element.text.strip())[1])

                        elif iw_name == '在看':
                            watching = int(re.split('[\(\)]', iw_element.text.strip())[1])

                        else:
                            want2watch = int(re.split('[\(\)]', iw_element.text.strip())[1])
                    
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

                        # 默认是热门标签
                        sortedby_page_path = {
                            '热门':"//div[@class='fleft Comments-sortby']/span",
                            '最新':"//div[@class='fleft Comments-sortby']/a"
                        }
                        
                        for sortedby_name, sortedby_path in sortedby_page_path.items():
                            # 先判断有没有超过600条数
                            if (iw_name == '看过' and watched > 600) or (iw_name == '在看' and watching > 600) or \
                                (iw_name == '想看' and want2watch > 600):
                                if sortedby_name != '热门':
                                    wait_for_show_up(
                                        driver, by_method=By.XPATH, 
                                        page_path=sortedby_path,
                                        click=True
                                    )

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
                                    creator = info_e.find_element(By.XPATH, f"./a")

                                    creator_text = creator.text
                                    ct = info_e.find_element(By.XPATH, f".//span[@class='comment-time ']").text
                                    ct = ct.strip()

                                    userid.append(creator_text), create_time.append(ct)

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
                                    'watch_status':watch_status, 'stars_comment':stars_comment, 'locations':locations, 'watched':[watched for i in create_time], 
                                    'watching':[watching for i in create_time], 'want2watch':[want2watch for i in create_time]
                                    })
                                
                                dataset = pd.concat((dataset, new_ds), ignore_index=True)
    
                                # 点击后页
                                if wait_for_show_up(
                                        driver, by_method=By.XPATH, 
                                        page_path=f"//a[@class='next' and text()='后页 >']",
                                        click=True, duration=100, sleep=2
                                ) is not None:
                                    page_cnt += 1
                                else:
                                    break
                            
                            if page_cnt == 0 and iw_name == '看过':
                                new_ds = pd.DataFrame(data={
                                    'create_time':None, 'given_drama_name':d, 'douban_drama_name':de_text, 
                                    'rating':rating, 'short_comment':'', 'creator':'', 'stars':'', 'watch_status':'', 'stars_comment':'未打星',
                                    'locations':'', 'watched':watched, 'watching':watching, 'want2watch':want2watch
                                    }, index=[0])
                                
                                dataset = pd.concat((dataset, new_ds), ignore_index=True)
                    
                    break # 跳出搜索列表循环

            if storage:
                # 去重存储
                dataset.drop_duplicates().to_csv(fpath, sep=',', encoding='utf-8', index=False)

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

    drama_list = [
        'C9特工','一舞倾城','七公主','上车家族','丫鬟大联盟','伙记办大事','傲娇与章经','十八年后的终极告白','十八年后的终极告白2.0','十月初五的月光',
        '双生陌生人','反黑路人甲','大酱园','失忆24小时','宝宝大过天','My Pet My Angal','我家无难事','把关者们','拳王','换命真相','星空下的仁医','木棘证人','机场特警','法言人',
        '清洁师','爱上我的衰神','痞子殿下','白色强人2','窃脑宅男','童时爱上你','美丽战场','荒诞剧团','超能使者','轻·功','迷网','逆天奇案','金宵大厦2','降魔的2.0','隐形战队',
        '青春本我','青春训练班','香港爱情故事','黄金万两','黄金有罪',
        '黯夜守护者', '法证先锋4','非凡三侠','叹息桥','战毒','飞虎之壮志英雄','刑侦日记',
        '黑金风暴','家族荣耀','廉政狙击','铁拳英雄'
    ]

    years = {
        '十月初五的月光':2021, '拳王':2021
    }

    vod_type = ['剧集'] * len(drama_list)
    page_limit = False # 目前豆瓣限制游客只能看前十页短评, 即使登录也只能爬600*3条短评

    dataset = None

    dataset = crawler(drama_list, vod_type=vod_type, release_years=years, page_limit=page_limit, storage=True, warm_up=True, page_load_strategy='normal',
                                  use_manager=False, headless=False, browser_name='Chrome', to_login=True, fpath='rating-0818.csv')

    # while True:
    #     ip = get_proxy_ip(invalid_ip=invalid_ip, proxy_type='https')
    #     if ip:
    #         try:
    #             dataset = crawler(drama_list, vod_type=vod_type, page_limit=page_limit, storage=True, warm_up=True, to_login=True,
    #                               use_manager=False, headless=False, browser_name='Chrome',ip=ip, fpath='rating-0818.csv', page_load_strategy='normal')
    #             break
    #         except Exception as e:
    #             # print(e)
    #             print('invalid ip: ', ip)

    #             invalid_ip.append(ip)
    #             continue
    #     else:
    #         break
    
    print(dataset)
