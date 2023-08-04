# 爬取给定影视列表的豆瓣评分和短评

from my_spider import *
from my_spider._common_config import *

def maxmize_window(driver, maximize=True, open_on_top_screen=True):
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


def crawler(driver, drama_list, page_limit=9):

    rating_dict = {}
    short_coment_dict = {}

    for d in tqdm(drama_list):
        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
            send_keys=d
        )

        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//input[@type='submit' and @value='搜索']", 
            click=True
        )

        for e in zip(
            wait_for_show_up(
                driver, by_method=By.XPATH, 
                # 找到和给定剧集匹配的标签
                page_path=f"//a[@class='title-text' and contains(text(), {d})]", index=-1
            ), 
            wait_for_show_up(
                driver, by_method=By.XPATH, 
                # 限制是中国香港的剧集
                page_path=f"//div[@class='meta abstract' and contains(text(), '中国香港')]", index=-1
            )
        ):
            if e[0] and e[1]:
                # 获取评分
                rating_dict[d] = wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    page_path="//span[@class='rating_nums']", 
                ).text

                e[0].click() # 点击进入详情页

                # 点击进入讨论区
                wait_for_show_up(
                    driver, by_method=By.XPATH, 
                    # 限制是中国香港的剧集
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
                                            index=-1
                                        )
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
                        
                short_coment_dict[d] = short_coment

                break

        # 清空搜索框
        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
        ).clear()
    
    driver.quit()
    print(rating_dict)
    print(short_coment_dict)


if __name__ == '__main__':
    drama_list = ['美丽战场', '大侠霍元甲', '射雕英雄传', '神雕侠侣']
    driver = get_driver('Chrome', page_load_strategy='eager', use_manager=True)
    douban_url = 'https://movie.douban.com/'

    driver = maxmize_window(driver)

    try:
        driver.get(douban_url)
        # 登录豆瓣
        login(driver)

        time.sleep(5) # 手动滑动验证码
        page_limit = 30 # 如果登录成功就采集30页的短评
    except:
        # 如果登录失败，就直接使用游客模式
        driver.get(douban_url)
        page_limit = 9 # 目前豆瓣限制游客只能看前十页短评

    crawler(driver, drama_list)
