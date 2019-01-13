import requests
import re
import concurrent
from bs4 import BeautifulSoup

list_base_url = 'https://eu.finalfantasyxiv.com/lodestone/playguide/db/item/?page='
item_base_url = 'https://eu.finalfantasyxiv.com/lodestone/playguide/db/item/'
max_page_id = 0
parsed_items = {}

list_page_url_regex = r'<li class=\"current\"><a href=\"https://eu\.finalfantasyxiv\.com/lodestone/playguide/db/item/\?page=(\d+)\">'
list_page_item_url_regex = r'<a href=\"\/lodestone\/playguide\/db\/item\/([a-f0-9]{11})\/\">'

# find highest pageid
page = requests.get('%s%i' % (list_base_url, 100000))

if page.status_code == 200:
    # REEE REGEX TO SEARCH HTML!!!!!!!!!
    m = re.search(list_page_url_regex, page.text)

    max_page_id = int(m.group(1))

    print("found max page id:", max_page_id)


def process_item(lds_id):
    item_page = requests.get("%s%s/" % (item_base_url, lds_id)).text
    item_page = BeautifulSoup(item_page, features='html.parser')

    item_img_url = item_page.find('img', attrs={'class': 'db-view__item__icon__item_image'})['src']
    item_name = item_page.find('h2', attrs={'class': 'db-view__item__text__name'}).text.strip()

    parsed_items[lds_id] = (item_name, item_img_url)


for id in range(1, max_page_id):
    url = "%s%i" % (list_base_url, id)

    list_page = requests.get(url).text

    print("Processing page", id, "of", max_page_id)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as exec:
        for match in re.findall(list_page_item_url_regex, list_page):
            exec.submit(process_item, match)
    

print("dumping items:")
with open('items.txt', "w+") as f:
    for k, v in parsed_items.items():
        name, url = v
        output = "%s,%s,%s" % (k, name, url)
        print(output)
        f.write(output + '\n')