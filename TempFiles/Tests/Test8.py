from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()
#path_to_chromedriver='C:/Inst/chromedriver.exe'
path_to_chromedriver ='/usr/bin/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
    executable_path=path_to_chromedriver,
    options=chrome_options)

#driver = webdriver.Chrome(chrome_options=options)
driver.get('http://nytimes.com')
print(driver.title)