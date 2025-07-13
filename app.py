from flask import Flask, render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from translations import texts  # ficheiro para tradução

app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-segura-123!'



# Configurações Cloudinary 
cloudinary.config(
    cloud_name='dnm3u3f1p',
    api_key='764794684413156',
    api_secret='K-nMTYb_8gXGKHoV9MXS2YQhI4k'
)

# Configurações MongoDB 
MONGO_URI = "mongodb+srv://artisaart:IjhtH858vRVACKWH@cluster0.rki0ea1.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client['artisaart']
encomendas_col = db['encomendas']

SENHA_ADMIN = "senha123" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submeter', methods=['POST'])
def submeter():
    nome = request.form['nome']
    email = request.form['email']
    descricao = request.form['descricao']
    medidas = request.form['medidas']
    material = request.form['material']
    imagem = request.files.get('imagem')

    imagem_url = None
    if imagem:
        result = cloudinary.uploader.upload(imagem)
        imagem_url = result.get('secure_url')

    encomenda = {
        'nome': nome,
        'email': email,
        'descricao': descricao,
        'medidas': medidas,
        'material': material,
        'estado': 'Pendente',
        'imagem_url': imagem_url
    }
    encomendas_col.insert_one(encomenda)
    flash("Encomenda submetida com sucesso! Receberá confirmação por email.")
    return redirect(url_for('index'))

@app.route('/encomendas', methods=['GET', 'POST'])
def ver_encomendas():
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == SENHA_ADMIN:
            session['logged_in'] = True
        else:
            return render_template('login.html', erro="Senha incorreta. Tente novamente.")

    if 'logged_in' not in session or not session['logged_in']:
        return render_template('login.html')

    encomendas = list(encomendas_col.find())
    return render_template('encomendas.html', encomendas=encomendas)

@app.route('/apagar/<id>', methods=['POST'])
def apagar_encomenda(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('ver_encomendas'))

    encomendas_col.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('ver_encomendas'))

@app.route('/atualizar/<id>', methods=['POST'])
def atualizar_estado(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('ver_encomendas'))

    novo_estado = request.form['estado']
    encomendas_col.update_one({'_id': ObjectId(id)}, {'$set': {'estado': novo_estado}})
    return redirect(url_for('ver_encomendas'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
