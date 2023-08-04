import os
import time
import json
from io import BytesIO

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.edge.options import Options as edge_options

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from lxml import etree

import pyautogui
from Crypto.Cipher import AES
import binascii
from tqdm.auto import tqdm
import numpy as np
