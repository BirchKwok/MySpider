# 爬取给定影视列表的豆瓣评分和短评

from my_spider import *
from my_spider._common_config import *

def maximize_window(driver, maximize=True, open_on_top_screen=True):
    if open_on_top_screen:
        driver.set_window_position(0, -1000)
    
    if maximize:
        driver.maximize_window()

    return driver


def json_load(fp):
    with open(fp, 'r', encoding='utf8') as f:
        return json.load(f)


def login(driver):
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
        send_keys=json_load('config.json')['douban_account']
    )

    # 填入密码
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//input[@id="password" and @class="account-form-input password" and @placeholder="密码" and @tabindex="3"]',
        click=True,
        send_keys=json_load('config.json')['douban_passwd']
    )

    # 点击登录
    wait_for_show_up(
        driver, by_method=By.XPATH, 
        page_path='//a[@class="btn btn-account btn-active" and text()="登录豆瓣"]',
        click=True
    )
    return driver


def dump2file(d, fp, encoding='utf-8'):
    with open(fp, 'w', encoding=encoding) as f:
        json.dump(d, f, ensure_ascii=False)


def load_json(fp, encoding='utf-8'):
    try:
        with open(fp, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        return 


def crawler(
    drama_list, 
    page_limit=9, # 刮削页数
    maximize=True, # 最大化浏览器窗口
    open_on_top_screen=True,  # 是否在第二屏幕打开
    storage=True, # 是否需要存储到文件
    rating_json_path='rating.json',  # 评分存储路径
    short_comment_json_path='short_comment.json',  # 短评存储路径
    warm_up=False, # 是否追加到文件最后
    use_manager=True, # 是否使用浏览器driver管理器
    page_load_strategy='eager', # driver加载网页策略
    new_window_each_session=False  # 是否每个会话都新开一个浏览器窗口
):
    """主程序"""
    douban_url = 'https://movie.douban.com/'

    if warm_up and storage:
        rating_dict = load_json(rating_json_path) or {}
        short_comment_dict = load_json(short_comment_json_path) or {}
    else:
        rating_dict = {}
        short_comment_dict = {}
    
    def getinto():
        driver = get_driver('Chrome', page_load_strategy=page_load_strategy, use_manager=use_manager)
        if maximize:
            driver = maximize_window(driver, open_on_top_screen=open_on_top_screen)
        driver.get(douban_url)
        return driver

    if not new_window_each_session:
        driver = getinto()

    for d in tqdm(drama_list):
        d = d.strip()
        if d in rating_dict.keys():
            continue

        if new_window_each_session:
            driver = getinto()

        time.sleep(np.random.randint(1, 3)) # 随机休眠

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
                    page_path=f"//a[@class='title-text']", index='all'
            )
        
        dramas_from = wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    # 首选是中国的剧集
                    page_path=f"//div[@class='meta abstract']", 
                    index='all'
            )
        
        if drama_es != [None] and dramas_from != [None]:
            for (de, df) in zip(drama_es, dramas_from):
                de_text = de.text
                df_text = df.text
                # 如果搜索结果不为空
                if (fuzz.partial_ratio(d, de_text) >= 75 or fuzz.partial_ratio(d, df_text) >= 75) and re.search('大陆|香港|台湾', df_text):
                    
                    # 获取评分
                    rate_element = wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path="//span[@class='rating_nums']", 
                    )

                    if rate_element is not None:

                        rating_dict[d] = {de_text:rate_element.text}
                    else:
                        rating_dict[d] = {de_text:None}

                    de.click() # 点击进入详情页

                    # 点击进入讨论区
                    wait_for_show_up(
                        driver, by_method=By.XPATH, 
                        page_path=f"//h2/i[contains(text(), '短评')]/following-sibling::span[@class='pl']/a[contains(text(), '全部')]",
                        click=True
                    )

                    # 采集所有的短评
                    short_coment = []

                    page_cnt = 0
                    while page_cnt <= page_limit:
                        time.sleep(np.random.randint(1, 4)) # 随机休眠
                        current_elements = wait_for_show_up(
                                                driver, by_method=By.XPATH, 
                                                page_path=f"//span[@class='short']",
                                                index='all'
                                            )
                        if current_elements == [None]:
                            break

                        short_coment.extend([i.text for i in current_elements])
                        # 点击后页
                        if wait_for_show_up(
                                driver, by_method=By.XPATH, 
                                page_path=f"//a[@class='next' and text()='后页 >']",
                                click=True, duration=1
                        ) is not None:
                            page_cnt += 1
                        else:
                            break
                    
                    short_comment_dict[d] = {de_text:short_coment}
                    break

            if storage:
                dump2file(rating_dict, rating_json_path), dump2file(short_comment_dict, short_comment_json_path)

            if new_window_each_session:
                driver.quit()
            else:
                wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
                ).clear() # 清空搜索框

    if not new_window_each_session:
        driver.quit()

    return rating_dict, short_comment_dict


if __name__ == '__main__':
    drama_list = ['美丽战场', '大侠霍元甲', '射雕英雄传', '神雕侠侣']
    page_limit = 9 # 目前豆瓣限制游客只能看前十页短评

    print(crawler(drama_list, page_limit=page_limit, storage=False))  # 不需要存储进硬盘
