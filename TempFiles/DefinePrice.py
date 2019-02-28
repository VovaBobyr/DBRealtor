import  re
str = ' 12 000 Kč za měsíc, včetně právního servisu'
str_new = re.findall(r'\d+', str)
price = ''
for i in str_new:
    price = price + i
price_int = int(price)
print(price_int)
