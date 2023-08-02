# 爬取给定影视列表的豆瓣评分

import sys
sys.path.append('.')
from my_spider import *
from my_spider._common_config import *

def maxmize_window(driver, maximize=True, open_on_top_screen=True):
    if open_on_top_screen:
        driver.set_window_position(0, -1000)
    
    if maximize:
        driver.maximize_window()

    return driver

if __name__ == '__main__':
    douban_url = 'https://movie.douban.com/'
    drama_list = ['美丽战场', '大侠霍元甲', '射雕英雄传', '神雕侠侣']

    driver = webdriver.Chrome()
    driver = maxmize_window(driver)
    driver.get(douban_url)

    rating_dict = {}

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

        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path=f"//a[@class='title-text' and contains(text(), {d})]", 
        )

        # 获取评分
        rating_dict[d] = wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//span[@class='rating_nums']", 
        ).text

        # 清空搜索框
        wait_for_show_up(
            driver, by_method=By.XPATH, 
            page_path="//input[@id='inp-query' and @name='search_text' and @placeholder='搜索电影、电视剧、综艺、影人']", 
        ).clear()
    
    driver.quit()
    print(rating_dict)
