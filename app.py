from flask import Flask, render_template, request, redirect
import requests, sys, re, os
from bs4 import BeautifulSoup
from json import JSONDecoder, dumps, load
from functools import partial
import concurrent.futures
from OpenSSL import SSL

app = Flask(__name__)

steamapikey = "FDBB490D0187D0AA68E36B5C28CC2657"
session = requests.session()
jar = requests.cookies.RequestsCookieJar()
jar.set('gclubsess', '5f28a079c80746c0f94263c8121aa074769f79da')  # 15.01.2021
session.cookies = jar

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*"
}

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html")


@app.route('/', methods=['POST', 'GET'])
def busca():
    if request.method == 'GET':
        stats = read_hash('buscas_recentes')       
        if len(stats) == 0:
            stats_fallen = get_stats(94)
            return render_template("fallen.html", player_stats=stats_fallen)
        else:
            return render_template("recents.html", players=stats)

    if request.method == 'POST':
        url_front = request.form['url_busca']
        dados_player = consulta_url(url_front)
        steamid64 = get_profile(url_front.split("/")[4])
        return render_template("index.html", player=dados_player, erro_player=erroPlayer, isAdmin=isAdmin, steam64orsteamid=steamid64, player_stats=player_stats)


@app.route('/partida/', methods=['GET'])
def red():
    return busca()

@app.route('/profiles/', methods=['GET'])
def red1():
    return busca()

@app.route('/partida/<matchid>/', methods=['GET'])
def grab_match_hash(matchid):
    if request.method == 'GET':
        checker = os.path.isfile(f'cache/{matchid}.txt')
        if checker:
            filetime = grab_file_time(matchid)
            if filetime == True:
                os.remove(f"cache/{matchid}.txt")
            else:
                match_players = read_hash(matchid, 1)
                return render_template("partida.html", players=match_players, steam64orsteamid=matchid)
        else:
            return busca()


@app.route('/profiles/<steamid>/', methods=['GET'])
def fuckoff(steamid):
    if request.method == 'GET':
        steam64 = get_profile(steamid)
        dados_player = consulta_url(f"http://steamcommunity.com/profiles/{steam64}")
        return render_template("index.html", player=dados_player, erro_player=erroPlayer, isAdmin=isAdmin, steam64orsteamid=steam64, player_stats=player_stats)


@app.route('/search', methods=['POST', 'GET'])
def search_mult():
    if request.method == 'GET':
        return busca()
    
    if request.method == 'POST':
        # remove os files com mais de 2 horas menos o buscas_recentes
        get_old_files("cache/")

        url_front = request.form['content']
        grab_players = get_multi_profiles(url_front)
        return render_template("partida.html", players=grab_players, steam64orsteamid=hashkey)


def grab_file_time(hashid):
    import datetime
    today = datetime.datetime.today()
    modified_date = datetime.datetime.fromtimestamp(
        os.path.getctime(f'cache/{hashid}.txt'))
    duration = today - modified_date

    if duration.seconds > 7200:
        return True
    else:
        return False


def get_old_files(path):
    import time, os
    now = time.time()

    for filename in os.listdir(path):
        filestamp = os.stat(os.path.join(path, filename)).st_ctime
        filecompare = now - 7200
        if filestamp < filecompare:
            if not 'buscas_recentes.txt' in filename:
                os.remove(f"cache/{filename}")


def get_hash():
    import random, string

    letters_and_digits = string.ascii_letters.lower() + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(5)))

    return result_str

# usado no read_hash
def json_parse(fileobj, decoder=JSONDecoder(), buffersize=2048):
    buffer = ''
    for chunk in iter(partial(fileobj.read, buffersize), ''):
        buffer += chunk
        while buffer:
            try:
                result, index = decoder.raw_decode(buffer)
                yield result
                buffer = buffer[index:].lstrip()
            except ValueError:
                # Not enough data to decode, read more
                break


def read_hash(hashid, defaut=0):
    if defaut == 1:
        with open(f'cache/{hashid}.txt') as f:
            return load(f)
    else:
        return list(json_parse(open(f'cache/{hashid}.txt')))


def get_profile(steamid):

    sixtyfourid = None

    if len(str(steamid)) != 17:
        vanitynameurl = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}"
        url = vanitynameurl.format(steamapikey, steamid)
        r = requests.get(url)
        if r.json()['response']['success'] == 1:
            sixtyfourid = r.json()['response']['steamid']
    else:
        sixtyfourid = steamid

    # sixtyfourid shoud hold the 64bit steamid or none if we couldn't match
    if sixtyfourid is None:
        return ""

    return sixtyfourid


def steamid_to_64bit(steamid):
    steam64id = 76561197960265728  # I honestly don't know where
    # this came from, but it works...
    id_split = steamid.split(":")
    # again, not sure why multiplying by 2...
    steam64id += int(id_split[2]) * 2
    if id_split[1] == "1":
        steam64id += 1
    return steam64id


def get_multi_profiles(text):
    global hashkey
    steam = re.findall(r'\STEAM_[0-5]:[01]:\d+', text)
    nicks = re.findall(r'"([^"]*)" STEAM_', text)

    names = [nomes for nomes in nicks]
    steams = [steamid_to_64bit(steamid) for steamid in steam]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = [executor.submit(consulta_url, url, nick, "True") for url, nick in zip(steams, names)]
    
        try:
           players = [(future.result()) for future in concurrent.futures.as_completed(future_to_url)]
        except Exception as exc:
            print('%r generated an exception:' % (exc))

        hashkey = get_hash()
        with open(f'cache/{hashkey}.txt', 'w') as json_file:
            json_file.write(dumps(players))
            json_file.close()

    return players


def getAdmin( url ):
    url = url.lower()
    lista = [ '76561198047241875', 'bruno1', 'hypochondriac1', '76561198888066058' ]
    for i in lista:
        if str( i ) in url:
            return True


def get_stats(userid):
    stats = session.get(f'https://gamersclub.com.br/api/box/history/{userid}', headers=headers)
    player_s = []
    if 'stat' in stats.json():
        for entry in stats.json()['stat']:
            case = {'stat': entry['stat'], 'value': entry['value']}
            player_s.append(case)
    else:
        return str("error")
    return player_s


def consulta_url(profile_url, nickname='', multiSearch='False'):
    global isAdmin
    global erroPlayer
    global player_stats
    player = {}

    if 'True' in multiSearch:
        page = session.get(f'https://gamersclub.com.br/buscar?busca=http://steamcommunity.com/profiles/{profile_url}', headers=headers, timeout=(10, None), stream=True)
        isAdmin = False
    else:
        page = session.get(f'https://gamersclub.com.br/buscar?busca={profile_url}', headers=headers, timeout=(5, None), stream=True)
        isAdmin = getAdmin(profile_url)

    soup = BeautifulSoup(page.text, "html.parser")
    page.close()

    # a classe jumbotron só aparece quando o jogador nao tem conta.
    no_account = soup.find(class_='jumbotron')
    if no_account:
        erroPlayer = True
        player_stats = False
        items = [item.next_sibling for item in soup.select(".jumbotron p strong")]

        if 'True' in multiSearch:
            player[u'name'] = nickname
        else:
            player[u'name'] = items[0]

        player[u'steamid'] = items[1]
        player[u'steam64'] = items[2]

        if items[3].isspace():
            player[u'vac'] = int(4)
            player[u'error_text'] = 'Jogador sem cadastro na steam!'
        else:
            player[u'vac'] = int(items[3])
            player[u'error_text'] = 'Jogador sem cadastro no site da Gamers Club.'

        player[u'avatar'] = soup.find('p').img['src']

        return player
    else:
        erroPlayer = False

        userid = soup.find(class_='gc-profile-user-id')
        if userid is not None:
            player[u'id'] = userid.get_text().split(": ")[1]
    
        if 'True' in multiSearch:
            player[u'name'] = nickname
        else:
            name = soup.find('div', 'gc-profile-user-container')
            if name is not None:
                player[u'name'] = name.get_text()

        steam = soup.find(class_='Button--steam')
        if steam is not None:
            player[u'steam'] = steam['href'].split("profiles/")[1]

        class_box = soup.find('div', class_='gc-profile-featured-box')
        if class_box:
            lvl = class_box.find_all("div", class_="gc-featured-item")[2:3]
            player[u'lvl'] = lvl[0].get_text().split()[0]

        image = soup.find('div', {"class": "gc-profile-avatar-img-container"})
        if image is not None:
            player[u'avatar'] = image.img['src']

        country = soup.find("span", {"class": "gc-profile-user-flag"})
        if country is not None:
            player[u'country'] = country['title']
            player[u'flag'] = country.img['src'][-6:]

        is_user_banned = False

        try:
            banned = soup.find("div", "center alert alert-danger").get_text()
            if banned:
                is_user_banned = True
                show_ban = False

                if 'VAC' in banned:
                    player[u'reason'] = banned
                    player[u'motivo_span'] = 2

                    show_ban = True
                else:
                    reason = soup.find("span", class_="primary-color").get_text()
                    player[u'reason'] = reason

                    if reason:
                        if 'Comportamento' in reason:
                            player[u'motivo_span'] = 0
                            show_ban = True
                        elif 'Entrar' in reason:
                            player[u'motivo_span'] = 1
                        else:
                            player[u'motivo_span'] = 3
                            show_ban = True

                    if show_ban == True:
                        ban = soup.find_all('strong')[1:2]
                        player[u'data_ban'] = ban[0].get_text()

                        duracao = soup.find_all('strong')[2:3]
                        player[u'banido_ate'] = duracao[0].get_text()
        except:
            is_user_banned = False

        player[u'isBanned'] = is_user_banned

        # nao quero que salve os players buscados no multi search
        if 'False' in multiSearch:
            player_stats = get_stats(player['id'])
            player['p_stats'] = list(player_stats)
        
            filename = "cache/buscas_recentes.txt"
            steamchecker = open(filename, 'r').read()
            qwert = re.search(f"{player['steam']}", steamchecker)

            if not qwert:
                statinfo = os.stat(filename)
                if statinfo.st_size >= 1048576:
                    file = open(filename, "r+")
                    file.truncate(0)
                    file.close()

                with open(filename, 'a') as json_file:
                    json_file.write(dumps(player))
                    json_file.close()

        return player


if __name__ == '__main__':
    # tratativa pra executar run certo se tiver no linux ou se tiver no windows testando
    if sys.platform == 'win32':
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    else:
        # original start server:
        # ssl path
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file('/etc/letsencrypt/archive/biqueirao.xyz/privkey4.pem')
        context.use_certificate_chain_file('/etc/letsencrypt/archive/biqueirao.xyz/fullchain4.pem')
        context.use_certificate_file('/etc/letsencrypt/archive/biqueirao.xyz/cert4.pem')
        context = ('/etc/letsencrypt/archive/biqueirao.xyz/cert4.pem', '/etc/letsencrypt/archive/biqueirao.xyz/privkey4.pem')
        app.run(host='0.0.0.0', port=443, debug=False, ssl_context=context)
