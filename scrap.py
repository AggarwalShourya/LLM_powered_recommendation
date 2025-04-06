from bs4 import BeautifulSoup
import requests
import pandas as pd

base_url="https://www.shl.com/solutions/products/product-catalog"
headers = {
    "User-Agent": "Mozilla/5.0"
}
webpage=requests.get(base_url,headers=headers).text
#print(webpage)

soup=BeautifulSoup(webpage,'lxml')
#print(soup.prettify())
#print(soup.find_all('h1')[0].text)
product_links=[]
data=[]
#for b in soup.find_all("a",class_="pagination__arrow",href=True):
for i in range(12):
    r=f"https://www.shl.com/solutions/products/product-catalog/?page=10&start={2*i}&type=2&type=2"
    base="https://www.shl.com"
    #print(b)
    web=requests.get(r).text
    webcontent=BeautifulSoup(web,'lxml')
    #print(webcontent)
    #break
    for a in webcontent.find_all("a",href=True):
        href=a['href']
        if "/solutions/products/product-catalog/view/" in href:
            #print(href)
            #print(base_url+href)
            #break
            product_links.append(base + href)
    #print(product_links)

for i in range(32):
    r=f"https://www.shl.com/solutions/products/product-catalog/?page=10&start={2*i}&type=2&type=1"
    base="https://www.shl.com"
    #print(b)
    web=requests.get(r).text
    webcontent=BeautifulSoup(web,'lxml')
    #print(webcontent)
    #break
    for a in webcontent.find_all("a",href=True):
        href=a['href']
        if "/solutions/products/product-catalog/view/" in href:
            #print(href)
            #print(base_url+href)
            #break
            product_links.append(base + href)
   # print(product_links)
#product_links = list(set(product_links))
    #print(len(product_links))

for url in product_links:
    details={}
    page=requests.get(url,headers=headers).text
    res=BeautifulSoup(page,'lxml')

    title=res.find('h1').text.strip()
    #print(title.text.strip() if title else "No title found")
    #break
    rows = res.find_all("div", {"class": "product-catalogue-training-calendar__row typ"})

    for row in rows:
        heading = row.find("h4")
        paragraph = row.find("p")
        if heading and paragraph:
            key = heading.text.strip().lower()
            val = paragraph.text.strip()
            details[key] = val

    #print(details)
    #print(len(details))
    #break
    data.append({
        "title":title,
        "Url":url,
        "description":details.get("description",""),
        "Assesment Length": details.get("assessment length",""),
        "job level":details.get("job levels",""),
        "languages":details.get("languages",""),
    })
df=pd.DataFrame(data)
df.to_csv("Data.csv",index=False)
print(df.head(5))
print(len(df))
#print("Total product pages found:", len(product_links))
#print("success")

# https://www.shl.com/solutions/products/product-catalog/view/account-manager-solution/