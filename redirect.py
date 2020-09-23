# ESTE REDIRECIONADOR RODA NA PORTA 80 E JOGA NA HTTPS, PODE DAR CONFLITO COM APACHE E OUTRO>
from flask import Flask,redirect, render_template
app = Flask(__name__)
@app.route('/')
def hello():
    return redirect("https://biqueirao.xyz", code=302)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
