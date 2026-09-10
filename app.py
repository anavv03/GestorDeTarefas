import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Garante que a pasta 'database' existe na raiz do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(BASE_DIR, 'database')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Configuração da Base de Dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "tarefas.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da Tabela no Banco de Dados
class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(200), nullable=False)
    feita = db.Column(db.Boolean, default=False)

# Criação do banco dentro do contexto da aplicação
with app.app_context():
    db.create_all()

# Rotas
@app.route('/')
def home():
    todas_as_tarefas = Tarefa.query.all()
    return render_template('index.html', lista_de_tarefas=todas_as_tarefas)

@app.route('/criar-tarefa', methods=['POST'])
def criar():
    texto_tarefa = request.form.get('conteudo_tarefa')
    if texto_tarefa:
        nova_tarefa = Tarefa(conteudo=texto_tarefa, feita=False)
        db.session.add(nova_tarefa)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/tarefa-feita/<int:id>')
def feita(id):
    tarefa = Tarefa.query.get_or_404(id)
    tarefa.feita = not tarefa.feita
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/eliminar-tarefa/<int:id>')
def eliminar(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)