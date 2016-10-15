
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import time
from urllib.request import Request, urlopen
import xlrd
import xlsxwriter

def clean_titles(title):
    clean_title = title.replace('--', '')
    clean_title = clean_title.replace('/', '-')
    clean_title = clean_title.replace('.', '')
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
def clean_element(element, type):
    if type == 'title':
        clean_element = element.replace("[text:",'')
        clean_element = clean_element.replace('[text:"','')
        clean_element = clean_element.replace('"', '')
        clean_element = clean_element.replace("'", '')
        clean_element = clean_element.replace("(", '')
        clean_element = clean_element.replace(")", '')
        #clean_element = clean_element.replace("'\f","")
        #clean_element = clean_element.replace('"\f', "")
        return clean_element
    else:
        clean_element = element.replace('"', '')
        clean_element = clean_element.replace("[",'')
        clean_element = clean_element.replace("]", '')
        clean_element = clean_element.replace("'", '')
        clean_element = clean_element.replace('text:', '')
        clean_element = clean_element.replace("number:", '')
        clean_element = clean_element.replace(' ', '')
    return clean_element

def build_urls(game_info_list):
    base_url = 'http://www.metacritic.com/game/'
    url = ''
    platform = ''
    temp = ''
    url_list = []
    platform_dict = {
        'PlayStation4':'playstation-4',
        'XboxOne':'xbox-one',
        'PlayStation3':'playstation-3',
        'Xbox360':'xbox-360',
        'PC':'pc',
        'WiiU':'wii-u',
        'Nintendo3DS':'3ds',
        'PlayStationVita':'playstation-vita',
        'iPhone':'ios',
        'PlayStation2':'playstation-2',
        'Xbox':'xbox',
        'Wii':'wii',
        'NintendoDS':'ds',
        'NintendoDSi':'ds',
        'GameCube':'gamecube',
        'Nintendo64':'nintendo-64',
        'GameBoyAdvance':'game-boy-advance',
        'PlayStationPortable':'psp',
        'Dreamcast':'dreamcast',
        'iPad':'ios'
    }

    for game in game_info_list:
        platform = game[1]
        try:
            url = base_url + platform_dict[platform] + '/'
        except:
            url = base_url + 'error' + '/'
        temp = str(game[0])
        url = url + clean_titles(temp)
        url_list.append(url)

    return url_list

def has_game_rating(tag):
    return tag.has_attr('itemprop')==re.compile('ratingValue')

run_num = 0
xl_name = ''
min = 1
max = 501

while(run_num < 73):
    xl_name = ''
    xl_name = 'Metacritic' + str(run_num) + '.xlsx'

    rdbook = xlrd.open_workbook('gamedata.xlsx')
    wrtbook = xlsxwriter.Workbook(xl_name)
    metaData = wrtbook.add_worksheet()
    ignData = rdbook.sheet_by_name('Sheet1')

    game_list = []
    game_pair = []
    game_info = ''
    game_titles = []
    titles_fixed = []
    url_list = []
    score_list = []
    game_info_list = [[]]

    min = min + 500
    max = max + 500

    for rows in range(min,max):
        try:
            game_info = ignData.row(rows)
            game_list.append(game_info)
        except IndexError:
            break;


    for games in game_list:
        game_pair = str(games).split(',')
        game_info_list.append(game_pair)

    #for titles in game_titles:
    #    titles_fixed.append(clean_titles(str(titles)))
    #print(titles_fixed)
    del game_info_list[0]

    for i in range(len(game_info_list)):
            for j in range(len(game_info_list[i])):
                    if j==0:
                        game_info_list[i][j] = clean_element(game_info_list[i][j],'title')
                    else:
                    #if(j!=0):
                        game_info_list[i][j] = clean_element(game_info_list[i][j],'element')

    url_list = build_urls(game_info_list)
    for url in url_list:
        print(url)

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
        except UnicodeEncodeError:
            valid_page = False


        if(valid_page):
            soup = BeautifulSoup(html, 'html.parser')
            tag = str(soup.find(itemprop=re.compile('ratingValue')))
            tag = tag.replace('<span itemprop="ratingValue">', '')
            tag = tag.replace("</span>", "")
            score_list.append(tag)
        else:
            score_list.append('failed')

    row = 0

    print(game_info_list)

    for score in score_list:
        #metaData.write(row,0,titles_fixed[row])
        metaData.write(row, 0, game_info_list[row][0])
        metaData.write(row, 1, game_info_list[row][1])
        metaData.write(row, 2, game_info_list[row][2])
        metaData.write(row, 3, game_info_list[row][3])
        metaData.write(row, 4,score)
        row += 1

    wrtbook.close()
    print('success!')
    time.sleep(900)
    run_num += 1