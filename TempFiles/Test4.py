from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen('http://www.pythonscraping.com/pages/warandpeace.html')
bs = BeautifulSoup(html, "html.parser")

#print(bs.get_text())
#print(bs.tagStack('span'))
#nameList = bs.findAll('span', {'class': 'green'})
#for name in nameList:
#    print(name.get_text())

#print(bs.findAll({'h1','h2','h3','h4','h5',}))

#titles = bs.find_all(['h1', 'h2','h3','h4','h5','h6'])
#print([title for title in titles])

#nameList = bs.find_all(text='the prince')
#print(len(nameList))

allText = bs.findAll(id='text')
allText = bs.findAll("", {"id":"text"})
print(allText[0].get_text)
