from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

chrome_options = Options()
chrome_options.add_argument("--headless")
