# Introdução ao Flask - Framework Python para Aplicações Web
# Requisições Web -> Get e Post
# Instalação do Flask -> pip install flask

from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import pymysql as my

app = Flask(__name__)
app.secret_key = '123456789'

def conectar():
    conexao = my.connect(
        host='localhost',
        user='root',
        password='',
        database='cadastro',
        cursorclass = my.cursors.DictCursor 
    )
    return conexao

def calculo(peso, altura):
    imc = peso / (altura * altura)
    return imc

def imc(imc_calculado):
    if imc_calculado < 18:
        return 'Abaixo do Peso!!!'
    elif imc_calculado <= 25:
         return 'Peso Normal!!!'
    elif imc_calculado <= 30:
        return 'Sobrepeso!!!'
    else:
        return 'Obesidade!!!'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cadastro', methods = ['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')
    elif request.method == 'POST':
        senha = request.form.get('senha')
        usuario = {
            'nome': request.form.get('nome'),
            'email': request.form.get('email'), 
            'senhaHash': bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        }
        cadastrou = False
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        sql = 'INSERT INTO clientes (nome, email, senha) VALUES (%s, %s, %s)'
        cursor.execute(sql, (usuario['nome'], usuario['email'], usuario['senhaHash']))
        conexao.commit()
        conexao.close()
        cadastrou = True
        return redirect(url_for('confirmaCadastro', cadastrou = cadastrou))
    except Exception as e:
        erro = True
        print(f'Houve um erro: {e}') 
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        conexao = conectar()
        cursor = conexao.cursor()
        sql = 'SELECT * FROM clientes WHERE email= %s'
        cursor.execute(sql, (email, ))
        usuario = cursor.fetchone()
        if usuario:
            senhaHash = usuario['senha']
            print(f'Usuário Logado: {usuario['nome']}')
            if bcrypt.checkpw(senha.encode('utf-8'), senhaHash.encode('utf-8')):
                session['usuario_nome'] = usuario['nome']
                session['usuario_id'] = usuario['id']
                return redirect(url_for('painelUsuario'))
            else:
                print('Senha Incorreta!!!')
                return redirect(url_for('login'))

@app.route('/confirma_cadastro')
def confirmaCadastro():
    return render_template('confirmaCadastro.html')

@app.route('/historico', methods= ['GET', 'POST'])
def historico():
    if request.method == 'GET':
        id_cliente = int(session['usuario_id'])
        print(f'id: {id_cliente}')
        conexao = conectar()
        cursor = conexao.cursor()
        sql = 'SELECT * FROM historico_imc WHERE id_cliente= %s'
        cursor.execute(sql, (id_cliente, ))
        historico = cursor.fetchall()
        print(historico)
        return render_template('historico.html', historico = historico)
    
@app.route('/calcular_imc', methods = ['GET', 'POST'])
def calcularImc():
    if request.method == 'GET':
        return render_template('calcularImc.html')
    elif request.method == 'POST':
        altura = float(request.form.get('altura'))
        peso = float(request.form.get('peso'))
        id_cliente = int(session['usuario_id'])
        print(f'id: {id_cliente}')
        imc_calculado = calculo(peso, altura)
        classificacao = str(imc(imc_calculado))
        print(imc_calculado)
        print(classificacao)
        try: 
            conexao = conectar()
            cursor = conexao.cursor()
            sql = 'INSERT INTO historico_imc (id_cliente, altura, peso, imc_calculado, classificacao) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (id_cliente, altura, peso, imc_calculado, classificacao))
            conexao.commit()
            conexao.close()
            return render_template('painelUsuario.html')
        except Exception as e:
            erro = True
            print(f'Houve um erro: {e}')

@app.route('/painel_usuario')
def painelUsuario():
    if session:
            return render_template('painelUsuario.html', session = session)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

app.run(debug=True)