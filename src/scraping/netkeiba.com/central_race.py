# coding: UTF-8
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup
import re


url = 'http://race.netkeiba.com/'
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

# get race list
# print('http://race.netkeiba.com/?pid=race_list&id=p' + datetime.now().strftime("%m%d"))
driver.get(url + '?pid=race_list&id=p0616')
soup = BeautifulSoup(driver.page_source, 'html.parser')
pathes = set()
for a in soup.find_all("a", href=re.compile("pid=race&id=")):
    pathes.add(a.get("href"))

# get each race info
result_array = []
for path in pathes:
    result = {}

    driver.get(url + path)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    race_info_web = soup.select('.data_intro')[0]

    race_data = race_info_web.select('.racedata')[0]
    race_info = {}
    race_info['round']    = race_data.dt.text
    race_info['name']      = race_data.dd.h1.text
    race_info['course']    = race_data.dd.select('p')[0].text
    race_info['condition'] = race_data.dd.select('p')[1].text

    race_otherdata = race_info_web.select('.race_otherdata')[0]
    race_info['type1']  = race_otherdata.select('p')[0].text
    race_info['type2']  = race_otherdata.select('p')[1].text
    race_info['bounty'] = race_otherdata.select('p')[2].text

    result['race'] = race_info

    race_result_table_rows = soup.select('.race_table_01.nk_tb_common > tbody > tr')
    race_result = []
    for row in race_result_table_rows:
        race_result_item = {}
        tds = row.select('td')
        if len(tds) == 0:
            continue
        race_result_item['rank']        = tds[0].text
        race_result_item['frame']       = tds[1].text
        race_result_item['number']      = tds[2].text
        race_result_item['name']        = tds[3].text
        race_result_item['age']         = tds[4].text
        race_result_item['impost']      = tds[5].text
        race_result_item['jockey']      = tds[6].text
        race_result_item['time']        = tds[7].text
        race_result_item['diff']        = tds[8].text
        race_result_item['popularity']  = tds[9].text
        race_result_item['odds']        = tds[10].text
        race_result_item['3f']          = tds[11].text
        race_result_item['corner_num']  = tds[12].text
        race_result_item['stable']      = tds[13].text
        race_result_item['weigth']      = tds[14].text
        race_result.append(race_result_item)

    result['rece_result'] = race_result

    payouts = []
    for table in soup.select('.pay_table_01'):
        for tr in table.select('tbody > tr'):
            payout_result = {}
            payout_result['type'] = tr.th.text
            horse_orders       = []
            payouts            = []
            popularity_numbers = []

            for order in tr.select('td')[0].contents:
                if str(order) != '<br/>':
                    horse_orders.append(str(order))

            for payout in tr.select('td')[1].contents:
                if str(payout) != '<br/>':
                    payouts.append(str(payout))

            for popularity in tr.select('td')[2].contents:
                if str(popularity) != '<br/>':
                    popularity_numbers.append(str(popularity))

            payout_results = []
            for i in range(len(horse_orders)):
                payout_results.append({'order': horse_orders[i], 'payout': payouts[i], 'popularity': popularity_numbers[i]})
            payout_result['result'] = payout_results

            payouts.append(payout_result)

    result['payouts'] = payouts

    corner_order = []
    for tr in soup.select('.result_table_02 > tbody > tr'):
        corner_order.append({'corner': tr.th.text, 'order': tr.td.text})
    result['corner_order'] = corner_order

    rap_time = []
    trs = soup.select('.result_table_03 > tbody > tr')
    distances = trs[0].select('th')
    rap1 = trs[1].select('td')
    rap2 = trs[2].select('td')
    for i in range(len(distances)):
        rap_time.append({'distance': distances[i].text, 'rap1': rap1[i].text, 'rap2': rap2[i].text})
    result['rap_time'] = rap_time

    print(result)
    print('========')
    result_array.append(result)
print(result_array)
driver.quit()
