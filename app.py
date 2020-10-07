from flask import Flask, render_template, request, redirect
from OpenSSL import SSL
from bs4 import BeautifulSoup
import requests, json
import sys

app = Flask(__name__)

#ssl path
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/etc/letsencrypt/archive/biqueirao.xyz/privkey2.pem')
context.use_certificate_chain_file('/etc/letsencrypt/archive/biqueirao.xyz/fullchain2.pem')
context.use_certificate_file('/etc/letsencrypt/archive/biqueirao.xyz/cert2.pem')
context = ('/etc/letsencrypt/archive/biqueirao.xyz/cert2.pem','/etc/letsencrypt/archive/biqueirao.xyz/privkey2.pem')

# steam api pra mudar de steam id para steam64
steamapikey = "FDBB490D0187D0AA68E36B5C28CC2657"
session = requests.session()
jar = requests.cookies.RequestsCookieJar()
jar.set( 'gclubsess','dd04fda5750445e80c3849e1c7fd78c343075d80' )
session.cookies = jar

def isInt(n):
    try:
       int(n)
       return True
    except ValueError:
       return False

def get_profile(steamid):
    sixtyfourid = None
    if not isInt(steamid) or len(str(steamid)) != 17:
        vanitynameurl = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}"
        url = vanitynameurl.format( steamapikey, steamid )
        r = requests.get( url )
        if r.json()['response']['success'] == 1:
            sixtyfourid = r.json()['response']['steamid']
    else:
        sixtyfourid = steamid

    # sixtyfourid shoud hold the 64bit steamid or none if we couldn't match
    if sixtyfourid is None:
       return ""

    return sixtyfourid

@app.route( '/<steamid>/', methods=['GET'] )
def fuckoff(steamid):
    if request.method == 'GET':
        steam64 = get_profile( steamid )
        dados_player = consulta_url( f"http://steamcommunity.com/profiles/{steam64}" )
        return render_template( "index.html", player=dados_player, erro_player=erroPlayer, isAdmin=isAdmin, steam64orsteamid=steam64, player_stats=player_stats )
  
@app.route('/', methods=['POST', 'GET'])
def busca():
    if request.method == 'GET':
        stats_fallen = get_stats(94)
        return render_template("fallen.html", player_stats=stats_fallen)

    if request.method == 'POST':
        url_front = request.form['url_busca']
        if url_front == "":
            return render_template("index.html")
        dados_player = consulta_url(url_front)
        steamid64 = get_profile(url_front.split("/")[4])                                                   # redirecionar sem mudar de pagina.
        return render_template("index.html", player=dados_player, erro_player=erroPlayer, isAdmin=isAdmin, steam64orsteamid=steamid64, player_stats=player_stats )

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html")

def getAdmin(url):
    url = url.lower()
    lista = ['76561198047241875', 'bruno1', 'hypochondriac1', '76561198888066058']
    for i in lista:
        if str(i) in url:
            return True

def get_stats( userid ):
    stats = session.get( f'https://gamersclub.com.br/api/box/history/{userid}' )
    player_s = []

    for entry in stats.json()['stat']:
        case = {'stat': entry['stat'], 'value': entry['value'] }
        player_s.append(case)

    return player_s

def consulta_url( profile_url ):
    player = {} # cria uma lista
    global erroPlayer
    global isAdmin
    global player_stats
    isAdmin = getAdmin(profile_url)

    page = session.get( f'https://gamersclub.com.br/buscar?busca={profile_url}' ) #http://steamcommunity.com/profiles/76561197960690195 steam id do fallen
    soup = BeautifulSoup( page.text, "html.parser" )

    # a classe jumbotron só aparece quando o jogador nao tem conta.
    has_account = soup.find( class_='jumbotron' )
    if has_account:
        erroPlayer = True

        # seleciona todos os p strong dentro do jumbotron 
        items = [item.next_sibling for item in soup.select(".jumbotron p strong")]
          
        # pega o nome do player
        player[u'name'] = items[0]

        # pega a steamid 
        player[u'steamid'] = items[1]

        # pega a steam64
        player[u'steam64'] = items[2]

        # pega o vac 
        if items[3].isspace( ):
            player[u'vac'] = int(4)
            player[u'error_text'] = 'Jogador sem cadastro na steam!'

        else:
            player[u'vac'] = int(items[3])
            player[u'error_text'] = 'Jogador sem cadastro no site da Gamers Club.'

        # pega o avatar do jogador.
        player[u'avatar'] = soup.find( 'p' ).img['src']

        # cria a msg do erro.

        return player
    else:
        erroPlayer = False
        # pega a id do player. 
        userid = soup.find( 'div', 'gc-profile-user-id' ).get_text().split(": ")[1]
        player[u'id'] = userid

        # pega o stats do player 
        player_stats = get_stats( userid )

        # pega o nome do player
        name = soup.find('div', 'gc-profile-user-container').get_text()
        player[u'name'] = name

        # verifica se a classe gc-profile-featured-box existe
        class_box = soup.find( 'div', class_='gc-profile-featured-box' )
        if class_box:
            lvl = class_box.find_all( "div", class_="gc-featured-item" )[2:3]

            # pega somente o numero do level o numero '20 Skill Level' somente o numero 20
            player[u'lvl'] = lvl[0].get_text().split()[0]
        
        # pega o avatar do jogador.
        image = soup.find( 'div', { "class": "gc-profile-avatar-img-container" } ).img['src']
        player[u'avatar'] = image

        # pega o nome do pais
        country = soup.find( "span", { "class": "gc-profile-user-flag" } )
        player[u'country'] = country['title']

        # pega a flag do pais
        player[u'flag'] = country.img['src'][-6:]

        # precisamos declarar isso empty para nao dar erro se o player nao tiver ban.
        #reason = ban_date = duraction = "" # achei q usaria. TBR

        # span_reason, 0 = 'BAN POR RACISMO ou discurso de odio', 1 = 'Entrar em contato com a GC (BAN retardado)', 2 = 'VAC', 3 = 'BANIDO POR CHEATING mas com texto diferente de hj em dia'
        # span_reason = -1 # achei q usaria. TBR

        is_user_banned = False

        # Criar o try pra nao dar merda
        try:
            # tenta acha o motivo do ban
            banned = soup.find( "div", "center alert alert-danger" ).get_text()

            # se encontrar a div o jogador esta banido.
            if banned:
                is_user_banned = True

                # ele esta banido, mas ainda nao encontramos a duraction e o ban_date
                show_ban = False

                # se a palavra 'VAC' aparecer no texto do banned

                if 'VAC' in banned:
                    player[u'reason'] = banned
                    player[u'motivo_span'] = 2

                    # nao temos a duracao e a data do ban.
                    show_ban = True
                else:
                    # pega o motivo do ban
                    reason = soup.find( "span", class_="primary-color" ).get_text()
                    player[u'reason'] = reason

                    if reason:
                        # verifica o motivo
                        if 'Comportamento' in reason:
                            player[u'motivo_span'] = 0
                            show_ban = True
                        elif 'Entrar' in reason:
                            player[u'motivo_span'] = 1
                        else:
                            player[u'motivo_span'] = 3
                            show_ban = True
                    
                    if show_ban == True:
                        # pega a data do ban
                        ban = soup.find_all( 'strong' )[1:2]
                        player[u'data_ban'] = ban[0].get_text()

                        # pega a duracao do ban
                        duracao = soup.find_all('strong')[2:3]
                        player[u'banido_ate'] = duracao[0].get_text()
        except:
            is_user_banned = False
        
        player[u'isBanned'] = is_user_banned
        return player

if __name__ == '__main__':
    #tratativa pra executar run certo se tiver no linux ou se tiver no windows testando
    if sys.platform == 'win32':
        app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)
    #else:
        #original start server:
        app.run(host='0.0.0.0',port=443, debug=False, ssl_context=context)
