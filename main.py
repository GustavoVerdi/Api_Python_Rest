from flask import jsonify, Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, Column, String, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import traceback
import requests

app = Flask(__name__)

try:
    db_connection = create_engine('postgresql://postgres:1234@192.168.15.83:5432/Cid')
    print("Conexão com o banco de dados estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

def consultar_receita(cnpj):
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

Base = declarative_base()

class Tempresa(Base):
    __tablename__ = 'tempresa'

    id = Column(Integer, primary_key=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    situacao = Column(String)
    nome = Column(String)
    tipo = Column(String)
    fantasia = Column(String)
    uf = Column(String(2))
    municipio = Column(String)
    logradouro = Column(String)
    natureza_juridica = Column(String)
    porte = Column(String)
    telefone = Column(String)
    atividade_principal = Column(String)
    numero_funcionarios = Column(Integer, nullable=True)  
    faturamento_anual = Column(Integer, nullable=True)  
    vendedor_responsavel = Column(String, nullable=True)  

@app.route('/inserir_cnpj', methods=['POST'])
def inserir_cnpj():
    try:
        cnpj = request.form.get('ncnpj')
        if not cnpj:
            return redirect(url_for('cadastrar_empresa', error_message="O CNPJ é obrigatório no corpo da solicitação."))
        receita_data = consultar_receita(cnpj)
        
        if not receita_data:
            return redirect(url_for('cadastrar_empresa', error_message="Não foi possível obter informações da Receita Federal para este CNPJ."))

        atividade_principal = receita_data.get("atividade_principal")
        atividade_principal_text = atividade_principal[0].get("text", "") if atividade_principal else ""

        tempresa = Tempresa(
            cnpj=receita_data.get("cnpj"),
            situacao=receita_data.get("situacao"),
            nome=receita_data.get("nome"),
            tipo=receita_data.get("tipo"),
            fantasia=receita_data.get("fantasia"),
            uf=receita_data.get("uf"),
            municipio=receita_data.get("municipio"),
            logradouro=receita_data.get("logradouro"),
            natureza_juridica=receita_data.get("natureza_juridica"),
            porte=receita_data.get("porte"),
            telefone=receita_data.get("telefone"),
            atividade_principal=atividade_principal_text
        )

        Session = sessionmaker(bind=db_connection)
        session = Session()

        existing_entry = session.query(Tempresa).filter(Tempresa.cnpj == tempresa.cnpj).first()
        
        if existing_entry:
            session.close()
            errorcpf_message = "Este CNPJ já está cadastrado no banco de dados."
            return redirect(url_for('cadastrar_empresa', errorcpf_message=errorcpf_message))

        session.add(tempresa)
        session.commit()
        session.close()

        return redirect(url_for('cadastrar_empresa', success_message="Dados inseridos com sucesso no banco de dados."))

    except Exception as e:
        traceback_str = traceback.format_exc()
        return redirect(url_for('cadastrar_empresa', error_message=f"Erro ao processar a solicitação: {e}"))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            nome_vendedor = request.form.get('vendedor_responsavel')
            Session = sessionmaker(bind=db_connection)
            session = Session()
            consulta = text("SELECT * FROM tempresa WHERE vendedor_responsavel LIKE :termo ORDER BY id ASC")
            resultados = session.execute(consulta, termo=f'%{nome_vendedor}%').fetchall()
            session.close()
            return render_template('index.html', resultados=resultados)

        except Exception as e:
            traceback_str = traceback.format_exc()
            return jsonify({"error": f"Erro ao processar a solicitação: {e}", "traceback": traceback_str}), 500
    else:
        try:
            Session = sessionmaker(bind=db_connection)
            session = Session()
            consulta = text("SELECT * FROM tempresa ORDER BY id ASC")
            resultados = session.execute(consulta).fetchall()
            session.close()
            return render_template('index.html', resultados=resultados)

        except Exception as e:
            traceback_str = traceback.format_exc()
            return jsonify({"error": f"Erro ao processar a solicitação: {e}", "traceback": traceback_str}), 500

@app.route('/cadastrar', methods=['GET'])
def cadastrar_empresa():
    error_message = request.args.get('error_message')
    success_message = request.args.get('success_message')
    errorcpf_message = request.args.get('errorcpf_message')
    return render_template('cadastroemp.html', error_message=error_message, errorcpf_message=errorcpf_message, success_message=success_message)

@app.route('/atualizar_empresa', methods=['POST'])
def atualizar_empresa():
    try:
        empresa_id = request.form.get('id')
        Session = sessionmaker(bind=db_connection)
        session = Session()
        empresa = session.query(Tempresa).filter(Tempresa.id == empresa_id).first()
        if not empresa:
            return jsonify({"error": "Empresa não encontrada."}), 404

        if request.form.get('numero_funcionarios'):
            empresa.numero_funcionarios = request.form.get('numero_funcionarios')
        if request.form.get('faturamento_anual'):
            empresa.faturamento_anual = request.form.get('faturamento_anual')
        if request.form.get('vendedor_responsavel'):
            empresa.vendedor_responsavel = request.form.get('vendedor_responsavel')

        session.commit()
        session.close()
        return "Dados da empresa atualizados com sucesso."

    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({"error": f"Erro ao atualizar a empresa: {e}", "traceback": traceback_str}), 500

if __name__ == '__main__':
    app.run(debug=True)
