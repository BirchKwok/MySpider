from ._common_config import *


def wait_for_show_up(
        driver, by_method=By.XPATH, page_path=None,
        duration=3, send_keys=None, click=False, sleep=0.5,
        roll_to_show=False, index=0
):
    """等待元素出现并点击或填充"""

    wait = WebDriverWait(driver, duration)
    elements = None

    if not roll_to_show:
        elements = wait.until(EC.presence_of_all_elements_located((by_method, page_path)))
    else:
        try:
            # 定位元素
            elements = driver.find_elements(by_method, page_path)
        except:
            # 判断元素是否存在
            if elements is None:
                # 元素不存在，向下滚动直到找到元素
                tik = time.time()
                tok = time.time()
                while True:
                    try:
                        elements = wait.until(EC.presence_of_all_elements_located((by_method, page_path)))
                        break
                    except Exception:
                        # 创建ActionChains对象
                        actions = webdriver.ActionChains(driver)

                        actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    finally:
                        tok = time.time()

                    if (tok - tik) > duration * 100:
                        break
    if click:
        elements[index].click()

    if send_keys:
        elements[index].send_keys(send_keys)

    time.sleep(sleep)
    return elements[index]


def move2center_screen(driver):
    """移动鼠标到页面中间"""
    import pyautogui

    # 获取页面的高度和窗口的高度
    page_height = driver.execute_script("return document.body.scrollHeight")

    # 计算鼠标应该移动到的垂直位置
    middle_point = -page_height // 2

    # 将鼠标移动到页面的中间位置
    driver.execute_script(f"window.scrollTo(0, {middle_point});")

    # 将鼠标移动到页面的中间位置，有随机偏移量，以确保不整齐排列
    pyautogui.moveTo((pyautogui.size()[0] // 2), middle_point)

    return pyautogui.position()


def scroll_screen(driver, click_offsets):
    """从屏幕中间开始滚动屏幕"""

    move2center_screen(driver)

    # 模拟鼠标滚动到目标坐标
    pyautogui.scroll(click_offsets)
    pyautogui.sleep(1)

    return pyautogui.position()


def move_element(driver, selector, click_offsets=10):
    """移动元素"""
    # 定位元素
    wait = WebDriverWait(driver, 10)
    current_element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
    cex = current_element.location.get('x')
    cey = current_element.location.get('y')
    middle_x, middle_y = scroll_screen(driver, click_offsets)

    x_offset = abs(abs(cex) - abs(middle_x))
    y_offset = abs(abs(cey) - abs(middle_y))
    # 4. 拖动元素到目标位置
    actions = webdriver.ActionChains(driver)
    actions.drag_and_drop_by_offset(current_element, x_offset, y_offset).perform()

    time.sleep(1)

    return pyautogui.position()
