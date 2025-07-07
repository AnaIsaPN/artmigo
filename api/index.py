from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name='dnm3u3f1p',
    api_key='764794684413156',
    api_secret='K-nMTYb_8gXGKHoV9MXS2YQhI4k'
)

app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-segura-123!'  # Necessário para sessão

DB_FILE = 'encomendas.db'

SENHA_ADMIN = "senha123"  # Altere para a senha que desejar

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS encomendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    medidas TEXT NOT NULL,
                    material TEXT NOT NULL,
                    estado TEXT DEFAULT 'Pendente',
                    imagem_url TEXT
                )''')
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO encomendas (nome, email, descricao, medidas, material, imagem_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, email, descricao, medidas, material, imagem_url))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/encomendas', methods=['GET', 'POST'])
def ver_encomendas():
    # Se já está autenticado na sessão, mostra as encomendas
    if 'logged_in' in session and session['logged_in']:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM encomendas")
        encomendas = c.fetchall()
        conn.close()
        return render_template('encomendas.html', encomendas=encomendas)
    
    # Se o método for POST, tenta autenticar a senha
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == SENHA_ADMIN:
            session['logged_in'] = True
            return redirect(url_for('ver_encomendas'))
        else:
            return render_template('login.html', erro="Senha incorreta. Tente novamente.")
    
    # Se não estiver autenticado, mostra formulário de login
    return render_template('login.html')

@app.route('/atualizar/<int:id>', methods=['POST'])
def atualizar_estado(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('ver_encomendas'))
    
    novo_estado = request.form['estado']
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE encomendas SET estado = ? WHERE id = ?", (novo_estado, id))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_encomendas'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# Vercel usa esta variável
handler = app
