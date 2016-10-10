
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
from urllib.request import Request, urlopen
import xlrd
import xlsxwriter

#url = 'http://www.metacritic.com/game/pc/overwatch'
#response = requests.get(url)
#html = response.content

def clean_titles(title):
    clean_title = title.replace('--', '')
    clean_title = clean_title.replace('/', '-')
    clean_title = clean_title.replace('  ',' ')
    clean_title = clean_title.replace(':','')
    clean_title = clean_title.replace("'", '')
    clean_title = clean_title.replace(' ', '-')
    clean_title = clean_title.replace('"', '')
    clean_title = clean_title.replace("[",'')
    clean_title = clean_title.replace("text", '')
    clean_title = clean_title.replace("number", '')
    clean_title = clean_title.replace("?", '')
    clean_title = clean_title.lower()
    return clean_title
def clean_element(element):
    clean_element = element.replace('"', '')
    clean_element = clean_element.replace("[",'')
    clean_element = clean_element.replace("]", '')
    clean_element = clean_element.replace('text:', '')
    clean_element = clean_element.replace("number:", '')
    return clean_element

def build_urls(titles_fixed):
    base_url = 'http://www.metacritic.com/game/pc/'
    url = ''
    url_list = []

    for titles in titles_fixed:
        url = base_url + titles
        url_list.append(url)

    return url_list

def has_game_rating(tag):
    return tag.has_attr('itemprop')==re.compile('ratingValue')


rdbook = xlrd.open_workbook('gamedata.xlsx')
wrtbook = xlsxwriter.Workbook('Metacritic.xlsx')
metaData = wrtbook.add_worksheet()
ignData = rdbook.sheet_by_name('Sheet3')
#metaData = workbook.add_sheet('Sheet6')

game_list = []
game_pair = []
game_info = ''
game_titles = []
titles_fixed = []
url_list = []
score_list = []
game_info_list = [[]]

for rows in range(ignData.nrows):
    game_info = ignData.row(rows)
    game_list.append(game_info)
#print(game_list)

for games in game_list:
    game_pair = str(games).split(',')
    game_info_list.append(game_pair)
    #game_info_list.append(str(games).split(","))
    game_titles.append(game_pair[0])
#print(game_info_list)

for titles in game_titles:
    titles_fixed.append(clean_titles(str(titles)))
print(titles_fixed)

del game_info_list[0]

for i in range(len(game_info_list)):
        for j in range(len(game_info_list[i])):
                game_info_list[i][j] = clean_element(game_info_list[i][j])

print(game_info_list)

url_list = build_urls(titles_fixed)
print(url_list)

valid_page = True

# metacritic parser
for urls in url_list:
    #req = Request('http://www.metacritic.com/game/pc/world-of-warcraft-legion', headers={'User-Agent': 'Mozilla/5.0'})
    valid_page = True
    try:
        req = Request(urls, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
    except HTTPError:
        valid_page = False
        #print('failed')

    if(valid_page):
        soup = BeautifulSoup(html, 'html.parser')
        tag = str(soup.find(itemprop=re.compile('ratingValue')))
        tag = tag.replace('<span itemprop="ratingValue">', '')
        tag = tag.replace("</span>", "")
        score_list.append(tag)
    else:
        score_list.append('failed')

row = 0

for score in score_list:
    metaData.write(row,0,game_titles[row])
    metaData.write(row, 1, game_info_list[row][1])
    metaData.write(row, 2, game_info_list[row][2])
    metaData.write(row, 3, game_info_list[row][3])
    metaData.write(row, 4,score)
    row += 1

wrtbook.close()

print('success!')