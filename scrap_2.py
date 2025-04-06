from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
import time

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
    r=f"https://www.shl.com/solutions/products/product-catalog/?page=10&start={12*i}&type=2&type=2"
    base="https://www.shl.com"
    #print(b)
    web=requests.get(r).text
    webcontent=BeautifulSoup(web,'lxml')
    time.sleep(0.2)
    #print(webcontent)
    #break
    for row in webcontent.select("tr[data-course-id]"):
        link_tag = row.select_one("td.custom__table-heading__title a")
        remote_td = row.select("td.custom__table-heading__general")[0]
        adaptive_td = row.select("td.custom__table-heading__general")[1]

        product_links.append({
            "url": base + link_tag["href"],
            "title": link_tag.text.strip(),
            "remote_testing": "Yes" if remote_td.select_one("span.catalogue__circle.-yes") else "No",
            "adaptive_irt": "Yes" if adaptive_td.select_one("span.catalogue__circle.-yes") else "No"
        })
 

for i in range(32):
    r=f"https://www.shl.com/solutions/products/product-catalog/?page=10&start={12*i}&type=2&type=1"
    base="https://www.shl.com"
    #print(b)
    web=requests.get(r).text
    webcontent=BeautifulSoup(web,'lxml')
    time.sleep(0.2)
    #print(webcontent)
    #break
    for row in webcontent.select("tr[data-course-id]"):
        link_tag = row.select_one("td.custom__table-heading__title a")
        remote_td = row.select("td.custom__table-heading__general")[0]
        adaptive_td = row.select("td.custom__table-heading__general")[1]

        product_links.append({
        "url": base + link_tag["href"],
        "title": link_tag.text.strip(),
        "remote_testing": "Yes" if remote_td.select_one("span.catalogue__circle.-yes") else "No",
        "adaptive_irt": "Yes" if adaptive_td.select_one("span.catalogue__circle.-yes") else "No"
    })

#product_links = list(set(product_links))
    #print(len(product_links))

for product in product_links:
    details={}
    url=product['url']
    title=product['title']
    remote_testing=product['remote_testing']
    adaptive=product['adaptive_irt']

    page=requests.get(url,headers=headers).text
    res=BeautifulSoup(page,'lxml')
    time.sleep(0.2)
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
        "remote_testing":remote_testing,
        "adaptive":adaptive
    })

df=pd.DataFrame(data)
df.to_csv("Data_test.csv",index=False)
print(df.head(5))
print(len(df))
#print("Total product pages found:", len(product_links))
#print("success")

# https://www.shl.com/solutions/products/product-catalog/view/account-manager-solution/