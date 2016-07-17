#coding=cp936
'''
Created on 20160715

@author: ChronoCorax
'''

def print_safe(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print('EXCEPT', s.encode('utf-8'))

# print_safe('\xf6');exit()


import re, json
from os import mkdir
from os.path import isdir, join, splitext, isfile

import requests


s = requests.Session()
host_url = 'http://www.hentai-foundry.com'
r = s.get(host_url + '/?enterAgree=1&size=1550')
print('Connected')

# r = s.post(host_url + '/site/filters', 
#            data='rating_nudity=3&rating_violence=3&rating_profanity=3&rating_racism=3&rating_sex=3&rating_spoilers=3&rating_yaoi=0&rating_yaoi=1&rating_yuri=0&rating_yuri=1&rating_teen=0&rating_guro=0&rating_furry=0&rating_beast=0&rating_male=0&rating_male=1&rating_female=0&rating_female=1&rating_futa=0&rating_other=0&filter_media=A&filter_order=date_new&filter_type=0')

# with open('a.html', 'wb') as f:
#     f.write(r.text.encode())
# 
# cookie_s = r.headers['Set-Cookie']
# 
# session_head = 'PHPSESSID='
# token_head = 'YII_CSRF_TOKEN='
# 
# session_loc = cookie_s.find(session_head) + len(session_head)
# session = cookie_s[session_loc:session_loc+32]
# 
# token_loc = cookie_s.find(token_head) + len(token_head)
# token = cookie_s[token_loc:token_loc+98]
# token2 = token[:40]
# 
# print(token2)

# print(token)

# import re
# res = re.findall(r'<input type="hidden" value="(.*)" name="YII_CSRF_TOKEN" />', r.text)
# token3 = res[0]


# r = s.post(host_url + '/site/filters',
#             headers = {'Cookie': session_head + session + ';' + token_head + token3 + ';'},
# #             headers = {'Cookie': session_head + session + ';'},
#            data = token_head + token2 + '&rating_nudity=3&rating_violence=3&rating_profanity=3&rating_racism=3&rating_sex=3&rating_spoilers=3&rating_yaoi=0&rating_yaoi=1&rating_yuri=0&rating_yuri=1&rating_teen=1&rating_guro=1&rating_furry=1&rating_beast=1&rating_male=0&rating_male=1&rating_female=0&rating_female=1&rating_futa=0&rating_other=0&filter_media=A&filter_order=date_new&filter_type=0')

# r = s.get('http://www.hentai-foundry.com/pictures/user/scerg/434973/Hermione')
# with open('c.html', 'wb') as f:
#     f.write(r.text.encode())

# r = s.get('http://www.hentai-foundry.com/pictures/user/gulavisual/432886/Aqua-Party')
# with open('q.html', 'wb') as f:
#     f.write(r.text.encode())
#     
# exit()


# import sys, io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


ddir = './download'

def w(s):
    l = []
    for c in s:
        if c.isalpha() or c.isdigit() or c == '.':
            l.append(c)
        elif c == '-' or c == '_' or c == ' ':
            l.append('_')
    return ''.join(l)

def legal_name(name):
    return name.replace(' ', '_').replace('\\', '').replace('/', '').replace(':', '').replace('*','').replace('?', '').replace('"', '').replace('<', '').replace('>','').replace('|', '')

def download(url, name, download_dir=ddir):
    if not isdir(download_dir): mkdir(download_dir)
    name = w(name)
    
    if isfile(join(download_dir, name)):
        print('file already exists')
    else:
        r = s.get(url, stream=True)
        with open(join(download_dir, name), 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    pass

def download_from_page(page_url, name, download_dir=ddir):
    r = s.get(host_url + page_url)
    res1 = re.findall('<center><img width="([0-9]*)" height="([0-9]*)" src="(.*)" alt="(.*)" /></center>', r.text)
    src = ''
    if res1:
        _, _, src, fname = res1[0]
    else:
        res2 = re.findall(r'<center><img onClick="this.src=&#039;(.*)&#039;;', r.text)
        fname = name
        if res2: src = res2[0]
    
    if src:
        _, ext = splitext(src)
        fname += ext
        download('http:' + src, fname, download_dir)
        print_safe('Downloaded ' + user_from_page(page_url) + '\'s ' + w(name))
    else:
        with open('%s.html' % w(name), 'wb') as f:
            f.write(r.text.encode())

def user_from_page(page_url):
    return re.findall('/user/(.*?)/', page_url)[0]

def download_from_res(res, sub_dir):
    for url, name in res:
        download_from_page(url, name, download_dir=join(ddir, sub_dir))
    print('Finished.')

def featured(page_limit=1):
    print('Grabbing featured pictures')
    res = []
    for i in range(page_limit):
        r = s.get(host_url + '/pictures/featured/page/%d' % i)
        res.extend(re.findall(r'<div class="thumbTitle"><a href="(.*)">(.*)</a></div>', r.text))
        print('featured page read: %d / %d' % (i + 1, page_limit))
    
    L = len(res)
    print('A total of %d pictures found.' % L)
    return {'#featured': [{'url': url, 'name': name, 'finished': 'false'} for url, name in res]}

def by_user(username):
    print('Grabbing pictures from', username)
    
    res = []
    
    url = host_url + '/pictures/user/%s' % username
    page = 1
    while True:
        r = s.get(url)
        res.extend(re.findall(r'<div class="thumbTitle"><a href="(.*)">(.*)</a></div>', r.text))
        
        print('user page read: %d' % page)
        page += 1
        
        next_match = re.findall(r'<li class="next"><a href="(.*)">Next &gt;</a></li>', r.text)
        if not next_match: break
        else:
            url = host_url + next_match[0]
    
    L = len(res)
    print('A total of %d pictures found.' % L)
    return {username: [{'url': url, 'name': name, 'finished': 'false'} for url, name in res]}
    
# r = s.get('http://www.hentai-foundry.com/pictures/user/scerg')
# with open('z.html', 'wb') as f:
#     f.write(r.text.encode())

mission_path = './mission.json'


class Mission(object):
    def __init__(self, path=mission_path):
        self._path = mission_path
        if not isfile(self._path):
            with open(self._path, 'w') as f: f.write('{}')
        
    def do(self):
        with open(self._path) as f:
            m = json.load(f)
        for user, pic_list in m.items():
            for pic in pic_list:
                if pic['finished'] == 'false':
                    download_from_page(pic['url'], pic['name'], download_dir=join(ddir, user))
                    pic['finished'] = 'true'
                    with open(self._path, 'w') as f:
                        json.dump(m, f, indent=4)
        return True
    
    def update(self, d):
        with open(self._path) as f:
            m = json.load(f)
        
        for k in d:
            if not k in m:
                m[k] = d[k]
                print('user', k, 'updated.')
        
        with open(self._path, 'w') as f:
            json.dump(m, f, indent=4)
    
    def reboot(self, flag='false'):
        with open(self._path) as f:
            m = json.load(f)
        for _, pic_list in m.items():
            for pic in pic_list:
                pic['finished'] = flag
        with open(self._path, 'w') as f:
            json.dump(m, f, indent=4)


fav_users = ['Sinn4u', 'Tarakanovich', 'Lavah', 'AngelusMortis',
         'ikelag', 'Nachtmahr', 'soranamae', 'Kerbo', 'Ipheli',
         'mimic', 'personalami', 'Evulchibi', 'vempire', 'Calm']

featured_users = ['Xanemonium', 'FelinaColibra', 'khantian', 'GENSHI', 'Doomsatan666', 'Clavicle', 'chisuzu', 'Commissioner', 'TheRealShadman', 'RuslaPusla', 'lionSpirit', 'Carbonoid', 'Dalehan', 'morana-twins', 'Li0nie', 'kiyo', 'cedargrove', 'Kassandra', 'Goozie', 'Qoppa', 'ThePhoenixNest', 'aka6', 'Zepht7', 'BooPeep', 'agawa', 'BlackChain', 'mooq-e', 'triplehex', 'Ocidias', 'Kaztor08', 'Lunareth', 'scerg', 'BaseDesire', 'kosmikophobia', 'evilkingtrefle', 'ohayougirls', 'mushroompus', 'finalcake', 'Suumunster', 'InCase', 'Suika', 'OrionM', 'PillowKisser', 'KABOS', 'ValeriP', 'MrDoodles', 'SunsetRiders7', 'Aen', 'lionxxxheart', 'DrGraevling', 'japes', 'CatCouch', 'atryl', 'gulavisual', 'Savvader', 'Foxxetta', 'Polyle', 'LoyProjectErotics', 'Nadill', 'BlackSunArt', 'Zumi', 'Ganassa', 'mister-mediocre', 'Haylox', 'Neryumo', 'Faymantra', 'elwinne', 'BlazingIfrit', 'Samasan', '200proof', 'duyumind', 'flick', 'sabudenego', 'ecoas', 'RoxyRex', 'DragonFU', 'mechanized', 'Kamina1978', 'Gmeen', 'mythComplex', 'thriller', 'SamCooper', 'Hijabolic', 'WBreaux', 'Kumbhker', 'bonete', 'Ragora', 'pablocomics', 'CandyBrat', 'Yoghurt', 'purr-hiss', 'carmessi', 'ZionAlexiel', 'quaedam', 'r_ex', 'Farty', 'cutepet', 'Evulchibi', 'MAD-Project', 'Suika-X', 'faustsketcher', 'tinkerbomb', 'Rishnea', 'kuroitenshi', 'xxoom', 'lasterk', 'Ottomarr', 'silverad0', 'pornthulhu', 'monorus', 'Janse', 'Nyuunzi', 'Delidah', 'ClassX', 'cyberunique', 'krisCrash', 'Calm', 'Keknep', 'dmfo', 'personalami', 'Turtlechan', 'eooo', 'TalBlaiser', 'Yinyue', 'muscarine', '34san', 'sbqnpdz', 'elementrexx', 'tentank', 'Boobdollz', 'SeanPatty', 'Manmonkee', 'thablackrook', 'the-depth-of-infamy', 'Owler', 'Baronet', 'Bauq', 'Mugensaku', 'SwainArt', 'kwatakun', 'Daemoria', 'VenneccaBlind', 'Clumzor', 'Sinten-de-Marth', 'Reynardine', 'X-Estacado', 'hizzacked', 'thedevil', 'Studio-Pirrate', 'Sparrow', 'JojoBanks', 'Gavrillo', 'QueenOfJuice', 'dillerkind', 'osato-kun', 'Sovushka', 'artofcarmen', 'barretxiii', 'Apocallisti', 'sienna', 'Velena', 'Tarakanovich', 'ShadowMist', 'euD', 'neongun', 'PROT', 'ghostfire', 'arcanux', 'Rino99', 'Spidu', 'VincentCC', 'Aedollon', 'WickedJ', 'MelkorMancin', 'soulfein', 'Ferres', 'Bloodfart', 'Candra', 'Aivelin', 'smutshaman', 'greengriffin', 'HentaiBro', 'Hombre-Blanco', 'KarasuH', 'Magnifire', 'Hagfish', 'Harmonist11', 'nihaotomita', 'AnimeFlux', 'Karbo', 'anotherartistmore', 'Avamon', 'yang', 'slugboxHF', 'D-rex', 'ackanime', 'DrSmolev', 'NozDraws', 'Kyder', 'T2death', 'emperpep', 'RUBAKA', 'qazieru', 'OptionalTypo', 'SatinMinions', 'kenshin187', 'KairuHentai', 'Bloodwise', 'GlanceReviver', 'bigbakunyuu', 'andr01d-art', '7th-Heaven', 'My_Pet_Tentacle_Monster', 'Figgylicious', 'ArbuzBudesh', 'TipodeIncognito', 'hopelessbohemian', 'latenightsexycomics', 'EvaSolo', 'Lucien', 'hentaipatriarch', 'ninecolor', 'dclzexon', 'Original-Botticella', 'JohnRussell', 'mavezar', 'aaaninja', 'Freako', 'Felox08', 'erotibot', 'PiratePup', 'Chris3000', 'Shunkaku', 'CheesecakesDraws', 'H-bum', 'AngelusMortis', 'Albatross', 'CherryInTheSun', 'Nocure', 'rrobbott', 'ZomgSami', 'Yellowroom', 'Salamandra', 'porcupine', 'Motolog', 'BlueCatDown', 'WillowyJenkins', 'Nachtmahr', 'NeoCoill', 'JoiXXX', 'Fantasybangcomix', 'NinjaKitty', 'nennanennanenna', 'Dieleth', 'Exile', 'marukanitel', 'Sfan', 'Z0NE', 'Whitebeads', 'MapleMoon', 'IKUgames', 'nnairda', 'TheKite', 'SinComix', 'Puppets', 'Freli', 'svoidist', 'R-Alchemist', 'kajinman', 'Zet13', 'Evanight', 'ryoimaru', 'Coppertonepretty', 'froly', 'HeadVoices', 'Sheepuppy', 'psudonym', 'ihai', 'maxblackrabbit', 'CaschLeCook', 'Contingency', 'Hmage', 'Amakuri', 'Boolyonzy', 'Graniem', 'radiatormother', 'Crisisbeat', 'soranamae', 'Ultamisia', 'nesoun', 'Vintem', 'JustinianKnight', 'uthstar01', 'Rukasu', 'Kaihlan', 'DOXOlove', 'helenamarkos81', 'SaintxTail', 'Buru', 'vempire', 'seepingooze']

# S = set()
# d = featured(20)
# for ju in d['#featured']:
#     S.add(user_from_page(ju['url']))
#  
# print(list(S))

# m = Mission()
# for user in featured_users:
#     m.update(by_user(user))


m = Mission()
while True:
    try:
        k = m.do()
    except Exception:
        print('Connection failed, rebooted.')
        k = False
    if k: break