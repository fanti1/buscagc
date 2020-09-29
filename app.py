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
  
@app.route('/', methods=['POST', 'GET'])
def busca():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        
        url_front = request.form['url_busca']
        if url_front == "":
            return render_template("index.html")
        dados_player = consulta_url(url_front)
        return render_template("index.html", player=dados_player, erro_player=erroPlayer, url_front=url_front)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html")

def consulta_url(profile_url):
    session = requests.session()
    jar = requests.cookies.RequestsCookieJar()
    jar.set('gclubsess','dd04fda5750445e80c3849e1c7fd78c343075d80')
    session.cookies = jar
    consulta = session.get(f'https://gamersclub.com.br/buscar?busca={profile_url}')
    soup = BeautifulSoup(consulta.text, 'html.parser')
    semconta = soup.find(class_='jumbotron')

    if semconta:
        global erroPlayer
        erroPlayer = True
        return "Jogador sem cadastro no site da Gamers Club."
    else:
        userid = soup.find('div', 'gc-profile-user-id').text
        name   = soup.find('div', 'gc-profile-user-container').text

        box = soup.find('div', class_='gc-profile-featured-box')
        if box:
            teste = box.find_all("div", class_="gc-featured-item")[2:3]
            nivel = teste[0].get_text()

            NivelSplit = nivel.split()

        image = soup.find('div', { "class": "gc-profile-avatar-img-container" }).img['src']

        bandeira = soup.find('span', { "class": "gc-profile-user-flag" })
        titulo = bandeira['title']
        
        teste = bandeira.img['src']
        country = teste[-6:]

        motivo = ""
        span = -1
        ban_date = ""
        duracao = ""

        IsUserBanned = False

        try:
            banido = soup.find('div', 'center alert alert-danger').get_text()

            if banido:
                IsUserBanned = True
                mostrar = False

                if "VAC" in banido:
                    motivo = banido
                    span = 2
                else:
                    motivo = soup.find("span", class_="primary-color").get_text()
                    if motivo:
  
                        if 'Comportamento' in motivo:
                            span = 0
                            mostrar = True
                        elif 'Entrar' in motivo:
                            span = 1
                        else:
                            span = 3
                            mostrar = True

                        if mostrar == True:
                            ban = soup.find_all('strong')[1:2]
                            dura = soup.find_all('strong')[2:3]

                            ban_date = ban[0].get_text()
                            duracao = dura[0].get_text()
        except:
            IsUserBanned = False
            pass

        player = {
            "id": userid.split(': ')[1],
            "name": name,
            "lvl": NivelSplit[0],
            "isBanned": IsUserBanned,
            "avatar": image,
            "motivo": motivo,
            "motivo_span": span,
            "data_ban": ban_date,
            "banido_ate": duracao,
            "nome_pais": titulo,
            "codigo_pais": country
        }

        erroPlayer = False
        return player

if __name__ == '__main__':
    #tratativa pra executar run certo se tiver no linux ou se tiver no windows testando
    if sys.platform == 'win32':
        app.run(host='0.0.0.0',port=5000, debug=True,threaded=True)
    else:
        app.run(host='0.0.0.0',port=443, debug=False, ssl_context=context, threaded=True)