from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager
from models import Atracao, Equipe, Evento, Exibicao, Locais, Pessoa, Polo, Tag, Usuario
from datetime import time, date, datetime

app = Flask(__name__)
app.secret_key = 'xavesecreta'
CORS(app)

lm = LoginManager()
lm.init_app(app)

# ------------------- UTIL -------------------
def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    return obj

def serialize_item(item):
    """Converte dict ou objeto para JSON serializável"""
    if isinstance(item, dict):
        d = item.copy()
    elif hasattr(item, 'to_dict_with_rel'):
        d = item.to_dict_with_rel()
    else:
        d = item.to_dict()

    for key, val in d.items():
        if isinstance(val, list):
            d[key] = [serialize_item(v) for v in val]
        else:
            d[key] = serialize_datetime(val)
    return d

# ------------------- ROTAS DE EVENTOS -------------------
@app.route('/api/eventos', methods=['GET'])
def get_eventos():
    eventos = Evento.getall_with_rel()
    return jsonify([serialize_item(e) for e in eventos])

# ------------------- ROTAS DE ATRACAO -------------------
@app.route('/api/atracoes', methods=['GET'])
def get_atracoes():
    atracoes = Atracao.getall_with_rel()

    polo_id = request.args.get("polo_id")
    data = request.args.get("data")  # formato YYYY-MM-DD

    # 🔎 filtro por polo
    if polo_id:
        atracoes = [a for a in atracoes if str(getattr(a, "polo_id", None)) == str(polo_id)]

    # 🔎 filtro por data
    if data:
        atracoes = [
            a for a in atracoes
            if hasattr(a, "evento") and a.evento and str(a.evento.data) == data
        ]

    return jsonify([serialize_item(a) for a in atracoes])

# ------------------- ROTAS DE EQUIPE -------------------
@app.route('/api/equipes', methods=['GET'])
def get_equipes():
    equipes = Equipe.getall_with_rel()
    return jsonify([serialize_item(e) for e in equipes])

# ------------------- ROTAS DE EXIBICAO -------------------
@app.route('/api/exibicoes', methods=['GET'])
def get_exibicoes():
    exibicoes = Exibicao.getall_with_rel()
    return jsonify([serialize_item(e) for e in exibicoes])

# ------------------- ROTAS DE LOCAIS -------------------
@app.route('/api/locais', methods=['GET'])
def get_locais():
    locais = Locais.getall_with_rel()
    return jsonify([serialize_item(l) for l in locais])

# ------------------- ROTAS DE POLOS -------------------
@app.route('/api/polos', methods=['GET'])
def get_polos():
    polos = Polo.getall_with_rel()
    return jsonify([serialize_item(p) for p in polos])

# ------------------- ROTAS DE PESSOA -------------------
@app.route('/api/pessoas', methods=['GET'])
def get_pessoas():
    pessoas = Pessoa.getall_with_rel()
    return jsonify([serialize_item(p) for p in pessoas])

# ------------------- ROTAS DE TAG -------------------
@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.getall_with_rel()
    return jsonify([serialize_item(t) for t in tags])

# ------------------- ROTAS DE USUARIO -------------------
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.getall_with_rel()
    return jsonify([serialize_item(u) for u in usuarios])

# ------------------- RODAR A API -------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
