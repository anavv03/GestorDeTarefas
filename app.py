import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_aqui'

# Garante que a pasta 'database' existe na raiz do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(BASE_DIR, 'database')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Configuração da Base de Dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "tarefas.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo Atualizado da Tarefa
class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(200), nullable=False)
    feita = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Criar tabelas
with app.app_context():
    db.create_all()

# Rota Home com suporte a Filtros
@app.route('/')
def home():
    filtro = request.args.get('filtro', 'todas')
    
    if filtro == 'pendentes':
        todas_as_tarefas = Tarefa.query.filter_by(feita=False).order_by(Tarefa.data_criacao.desc()).all()
    elif filtro == 'concluidas':
        todas_as_tarefas = Tarefa.query.filter_by(feita=True).order_by(Tarefa.data_criacao.desc()).all()
    else:
        todas_as_tarefas = Tarefa.query.order_by(Tarefa.data_criacao.desc()).all()
        
    return render_template('index.html', lista_de_tarefas=todas_as_tarefas, filtro_atual=filtro)

# Rota para Criar Tarefa com Validação de Inputs
@app.route('/criar-tarefa', methods=['POST'])
def criar():
    texto_tarefa = request.form.get('conteudo_tarefa', '').strip()
    
    if not texto_tarefa:
        flash('Não é possível adicionar uma tarefa vazia!', 'danger')
    else:
        nova_tarefa = Tarefa(conteudo=texto_tarefa, feita=False)
        db.session.add(nova_tarefa)
        db.session.commit()
        flash('Tarefa adicionada com sucesso!', 'success')
        
    return redirect(url_for('home'))

# Rota para Editar Tarefa
@app.route('/editar-tarefa/<int:id>', methods=['POST'])
def editar(id):
    tarefa = Tarefa.query.get_or_404(id)
    novo_texto = request.form.get('conteudo_editado', '').strip()
    
    if not novo_texto:
        flash('O texto da tarefa não pode ficar vazio!', 'warning')
    else:
        tarefa.conteudo = novo_texto
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'info')
        
    return redirect(url_for('home'))

# Rota para Alternar Concluída/Pendente
@app.route('/tarefa-feita/<int:id>')
def feita(id):
    tarefa = Tarefa.query.get_or_404(id)
    tarefa.feita = not tarefa.feita
    db.session.commit()
    msg = 'Tarefa marcada como concluída!' if tarefa.feita else 'Tarefa marcada como pendente!'
    flash(msg, 'info')
    return redirect(url_for('home'))

# Rota para Eliminar Tarefa
@app.route('/eliminar-tarefa/<int:id>')
def eliminar(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa eliminada!', 'danger')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)