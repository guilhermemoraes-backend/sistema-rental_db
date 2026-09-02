import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/")
def home():
    return jsonify({"mensagem": "API Rental Eventos rodando com sucesso!"})

# 1 - Rota de Autenticação (Login - Item 4 do requisito)
@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")
    
    usuario = supabase.table("usuarios").select("*").eq("email", email).eq("senha", senha).execute()
    
    if len(usuario.data) > 0:
        return jsonify({"status": "sucesso", "usuario": usuario.data[0]}), 200
    return jsonify({"status": "erro", "mensagem": "Credenciais inválidas"}), 401

# 2 - Rota para listar Equipamentos (Item 6.1.1)
@app.route("/equipamentos", methods=["GET"])
def listar_equipamentos():
    resposta = supabase.table("equipamentos").select("*").execute()
    return jsonify(resposta.data), 200

# 3 - Rota de Registro de Avaria e Bloqueio (Funcionalidade Extra)
@app.route("/avarias", methods=["POST"])
def registrar_avaria():
    dados = request.json
    # Espera: id_equipamento, id_usuario, nivel_dano, descricao_avaria
    
    # Grava o registro da avaria
    avaria = supabase.table("registro_avarias").insert({
        "id_equipamento": dados["id_equipamento"],
        "id_usuario": dados["id_usuario"],
        "data_registro": "now()",
        "nivel_dano": dados["nivel_dano"],
        "descricao_avaria": dados["descricao_avaria"]
    }).execute()

    # Se o dano for Grave ou Danificado, bloqueia o equipamento automaticamente
    if dados["nivel_dano"].lower() in ["grave", "danificado"]:
        supabase.table("equipamentos").update({
            "estado_conservacao": "Danificado",
            "status_disponibilidade": "Bloqueado"
        }).eq("id_equipamento", dados["id_equipamento"]).execute()

    return jsonify({"status": "Avaria registrada e equipamento atualizado com sucesso!"}), 201

if __name__ == "__main__":
    app.run(debug=True)