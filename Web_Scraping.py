from urllib.error import URLError
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests


url = "https://www.allrecipes.com/recipes/"
Client = urlopen(url)
html_page = Client.read()
Client.close()

page_soup = BeautifulSoup(html_page,'html.parser')

rows = page_soup.findAll("div", {"class" : "col-container"})
#print(len(rows))
#print(BeautifulSoup.prettify(rows[0]))

#row = rows[0]

#recipie_name = row.findAll("div",{"class" : "all-categories-col"})
#print(recipie_name[0].text)

page_link = []
for row in rows:
    for link in row.findAll("a", href=True):
        page_link.append(link['href'])

#print(page_link)

#containers = []
#for link in page_link:
#link = page_link[0]
page = page_link
page_link = []
for link in page:
    Client = urlopen(link)
    html_page = Client.read()
    Client.close()

    page_soup = BeautifulSoup(html_page, 'html.parser')

    rows = page_soup.findAll("div", {"class": "fixed-grid"})

    #print(BeautifulSoup.prettify(rows[0]))
    for row in rows:
        for link in row.findAll("a", href=True):
            page_link.append(link['href'])

#print(page_link)

final_link = []
for link in page_link:
    s = link.split("/")
    if "recipe" in s:
        final_link.append(link)

#print(final_link)
print(len(final_link))

final_link.reverse()

filename = "Final_Scrape.csv"

headers = "Recipe Name,     Image Link,     Ingredients \n"

f = open(filename, "w", encoding="utf-8")

f.write(headers)

for i in range(len(final_link)):
    print(i)
    try:
        uClient = urlopen(final_link[i])
        page_html = uClient.read()
        uClient.close()

        page_soup = BeautifulSoup(page_html, "html.parser")

        recipe_name = page_soup.find('h1').text

        image = page_soup.find('div', {"class": "image-container"})
        image_link = image.div["data-src"]

        Ingredients = page_soup.find('ul', attrs={'class': 'ingredients-section'}).text.strip()
        Ingredients = " ".join(line.strip() for line in Ingredients.split("\n"))

        f.write(recipe_name + ",    " + image_link + ",     " + Ingredients + "\n")

    except (AttributeError, TypeError, KeyError, URLError):
        continue

f.close()

#https://www.allrecipes.com/recipe/10402/the-best-rolled-sugar-cookies/