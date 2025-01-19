import json, re, requests
from bs4 import BeautifulSoup, NavigableString, TemplateString
from utils.utils import get_IO_path

def get_tips():
    raw_tip_html = requests.get('https://mzh.moegirl.org.cn/Phigros').text
    ol_list = BeautifulSoup(raw_tip_html, 'html.parser').find(attrs={'class':"mw-collapsible mw-collapsed wikitable"}).find_all('ol')
    tip_info = {}
    for x in ol_list:
        if not ('class' in x.attrs.keys() and x.attrs['class'] == ['references']): 
            group_name = re.sub(r'\[(.*?)\]','',x.find_previous('b').get_text(types=(NavigableString, TemplateString))).strip()
            tips = []
            for y in x:
                if y.name == 'li':
                    single_tip = y.get_text(types=(NavigableString, TemplateString)).strip()
                    single_tip = re.sub(r'引用错误：没有找到(.*)标签','',single_tip)
                    single_tip = re.sub(r'\[(.*?)\]','',single_tip)
                    tips.append(single_tip)
            tip_info[group_name] = tips

    with open(get_IO_path("phigros_tips", "json"), 'w', encoding='utf-8') as f: f.write(json.dumps(tip_info, indent = 4, ensure_ascii = False))

def get_version():
    raw_version_html = requests.get('https://mzh.moegirl.org.cn/Phigros/谱面信息').text
    ver_text = re.search(r'本页面现已更新至(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日更新的(?P<version>.*)版本。',raw_version_html)
    info = {
        'version':ver_text.group('version'),
        'date':{
            'year':int(ver_text.group('year')),
            'month': int(ver_text.group('month')),
            'day': int(ver_text.group('day')),
        }
    }
    with open(get_IO_path("phigros_version_info", "json"), 'w', encoding='utf-8') as f: f.write(json.dumps(info, indent = 4, ensure_ascii = False))

def get_song_list():
    def parse(st):
        return str(st).strip() if st else "" if st is None else "undefined"

    ul_data = BeautifulSoup(requests.get('https://mzh.moegirl.org.cn/Phigros/谱面信息').text,'html.parser').find_all('table', class_='wikitable')
    data_list = {}
    for idx, item in enumerate(ul_data):
        if idx+1:
            tds = item.find_all('td')
            song = re.sub(r'\[\d+\]','',item.th.get_text(types=(NavigableString, TemplateString)))
            try: illustration = tds[0].a.img.get('src')
            except: illustration = 'undefined'
            illustration_big = illustration.replace('thumb/','').rsplit('/',1)[0]
            chapter = item.find('td', string="所属章节").find_next("td").get_text(types=(NavigableString, TemplateString))
            bpm = item.find('td', string="BPM").find_next("td").get_text(types=(NavigableString, TemplateString))
            composer = re.sub(r'\[\d+\]','',item.find('td', string="曲师").find_next("td").get_text(types=(NavigableString, TemplateString)))
            length = item.find('td', string="长度").find_next("td").get_text(types=(NavigableString, TemplateString))
            illustrator = re.sub(r'\[\d+\]','',item.find('td', string="画师").find_next("td").get_text(types=(NavigableString, TemplateString)))
            chart = {}
            if not item.find('td', string="EZ") is None:
                current = item.find('td', string="EZ").find_next('td')
                ez_level = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                ez_difficulty = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                ez_combo = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                ez_charter = re.sub(r'\[\d+\]','',current.get_text(types=(NavigableString, TemplateString)))
                chart["EZ"] = {"level": parse(ez_level), "difficulty": parse(ez_difficulty), "combo": parse(ez_combo), "charter": parse(ez_charter)}
            else:
                ez_level, ez_difficulty, ez_combo, ez_charter = 0, 0, 0, 0

            if not item.find('td', string="HD") is None:
                current = item.find('td', string="HD").find_next('td')
                hd_level = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                hd_difficulty = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                hd_combo = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                hd_charter = re.sub(r'\[\d+\]','',current.get_text(types=(NavigableString, TemplateString)))
                chart["HD"] = {"level": parse(hd_level), "difficulty": parse(hd_difficulty), "combo": parse(hd_combo), "charter": parse(hd_charter)}
            else:
                hd_level, hd_difficulty, hd_combo, hd_charter = 0, 0, 0, 0

            if not item.find('td', string="IN") is None:
                current = item.find('td', string="IN").find_next('td')
                in_level = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                in_difficulty = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                in_combo = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                in_charter = re.sub(r'\[\d+\]','',current.get_text(types=(NavigableString, TemplateString)))
                chart["IN"] = {"level": parse(in_level), "difficulty": parse(in_difficulty), "combo": parse(in_combo), "charter": parse(in_charter),}
            else:
                in_level, in_difficulty, in_combo, in_charter = 0, 0, 0, 0

            if not item.find('td', string="Legacy") is None:
                current = item.find('td', string="Legacy").find_next('td')
                lc_level = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                lc_difficulty = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                lc_combo = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                lc_charter = re.sub(r'\[\d+\]','',current.get_text(types=(NavigableString, TemplateString)))
                chart["Legacy"] = {"level": parse(lc_level), "difficulty": parse(lc_difficulty), "combo": parse(lc_combo), "charter": parse(lc_charter),}
            else:
                lc_level, lc_difficulty, lc_combo, lc_charter = 0, 0, 0, 0

            if not item.find('td', string="AT") is None:
                current = item.find('td', string="AT").find_next('td')
                at_level = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                at_difficulty = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                at_combo = current.get_text(types=(NavigableString, TemplateString))
                current = current.find_next("td")
                at_charter = re.sub(r'\[\d+\]','',current.get_text(types=(NavigableString, TemplateString)))
                chart["AT"] = {"level": parse(at_level), "difficulty": parse(at_difficulty), "combo": parse(at_combo), "charter": parse(at_charter)}
            else:
                at_level, at_difficulty, at_combo, at_charter = 0, 0, 0, 0
            if parse(song) == "Another Me":
                song = "Another Me (Rising Sun Traxx)" if parse(composer) == "Neutral Moon" else "Another Me (KALPA)"
            if parse(song) == "The Mountain Eater from MUSYNC": song = "The Mountain Eater"
            if parse(song).find('Cipher') != -1: song = 'Cipher: /2&//<|0'
            data_list[parse(song)] = {"song": parse(song), "illustration": parse(illustration), "illustration_big": parse(illustration_big),
                "chapter": parse(chapter), "bpm": parse(bpm), "composer": parse(composer), "length": parse(length), "illustrator": parse(illustrator),
                "chart": chart}
            
    data = json.dumps(data_list, indent = 4, ensure_ascii = False)
    with open(get_IO_path("phigros_song_list", "json"), 'w', encoding='utf-8') as f: f.write(data)

def get_data():
    get_tips()
    get_version()
    get_song_list()