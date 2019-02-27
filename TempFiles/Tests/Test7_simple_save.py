import os
import shutil
import requests
import sys

link_page = "https://www.sreality.cz/hledani/prodej/byty"
# print("Inside link: " + link_page)
direct_link = ''
inside_page = requests.get(link_page)
inputfile = "C:/Learning/Python/DBRealtor/TempFiles/simple_save.html"
myfile_inside = open(inputfile, mode="w", encoding="latin_1")
myfile_inside.write(inside_page.text)
myfile_inside.close()