from flask import Flask, render_template, redirect, url_for, flash, request, session
import os
import mercadopago
from flask import jsonify
from mercadopago import SDK


app = Flask(__name__)
app.secret_key = 'senha-super-secreta'  # segurança mínima

USUARIO = 'admin'
SENHA = '1234'



#------------------pagamento------------------------------------------
# Token e URL pública
ACCESS_TOKEN = "APP_USR-1522476758336723-052612-4622dc918fca525f5df25c6d9d2f9daf-2036286280"
#NGROK_URL = "https://67f8-186-201-223-74.ngrok-free.app"
NGROK_URL = "https://socialevolution.onrender.com"

# Instancia global do SDK (evita recriar a cada requisição)
sdk = SDK(ACCESS_TOKEN)

@app.route("/create_preference", methods=["POST"])
def create_preference():
    try:
        data = request.get_json()
        produto_id = int(data.get("produto_id"))

        produto = buscar_produto_por_id(produto_id)
        if not produto:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        
        print("Imagem do produto:", f"{NGROK_URL}/static/img/produtos/{produto['imagem']}")
        preference_data = {
        "items": [
                {
                    "title": produto["nome"],
                    "quantity": 1,
                    "unit_price": float(produto["preco"]),
                    "currency_id": "BRL",
                    "picture_url": f"https://socialevolution.onrender.com/static/img/produtos/{produto['imagem']}"
                }
            ],
            
            "back_urls": {
                "success": f"{NGROK_URL}/success",
                "failure": f"{NGROK_URL}/failure",
                "pending": f"{NGROK_URL}/pending"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response.get("response", {})

        if "init_point" not in preference:
            return jsonify({"error": "Erro ao criar link de pagamento"}), 500

        return jsonify({"init_point": preference["init_point"]})

    except Exception as e:
        print("Erro ao criar preferência:", e)
        return jsonify({"error": str(e)}), 500
    
#--------------------------fim do pagamento------------------------------------------
#----------resposta do pagamento----------------------------------------------------
@app.route("/success")
def success():
    return "Pagamento aprovado! Obrigado pela compra."

@app.route("/failure")
def failure():
    return "Pagamento cancelado ou falhou."

@app.route("/pending")
def pending():
    return "Pagamento pendente."
#----------fim resposta do pagamento--------------------------------------------------

@app.before_request
def redirect_to_https():
    if not request.is_secure and not app.debug:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)
    
    
    
categorias = {
    "Calças Esporte Fino": [
        {"id": 1, "nome": "Calça Branco Gelo", "preco": 5, "imagem": "BrancoGelo.jpeg", "descricao": "Calça elegante na cor branco gelo."},
        {"id": 2, "nome": "Calça Cinza Escuro", "preco": 110.0, "imagem": "Cinza.jpeg", "descricao": "Calça elegante na cor Cinza Claro."},
        {"id": 3, "nome": "Calça Branco Pelora", "preco": 120.0, "imagem": "Calca_Branco_Perola.jpeg", "descricao": "Calça elegante na cor branco gelo."},
        {"id": 4, "nome": "Calça Cinza Claro", "preco": 110.0, "imagem": "Calca_Cinza_Claro.jpeg", "descricao": "Calça elegante na cor Cinza Claro."}
    ],
    "Ternos Slim Fit ": [
        {"id": 5, "nome": "Terno Branco", "preco": 399.90, "imagem": "BrancoFrente.jpeg", "descricao": "Terno branco elegante com corte ajustado."},
        {"id": 6, "nome": "Terno Cinza", "preco": 389.90, "imagem": "Terno_Branco_Costa.jpeg", "descricao": "Terno cinza moderno, ideal para eventos formais."},
        {"id": 7, "nome": "Terno Cinza", "preco": 389.90, "imagem": "CinzaFrente.jpeg", "descricao": "Terno cinza moderno, ideal para eventos formais."},
        {"id": 8, "nome": "Terno Branco", "preco": 399.90, "imagem": "Terno_Cinza_Costa.jpeg", "descricao": "Terno branco elegante com corte ajustado."}
        
    ],
    "Conjunto Clássico": [
        {"id": 9, "nome": "Calça Jeans & Camisa Xumbo", "preco": 5, "imagem": "Jeans_Preta.jpeg", "descricao": "Conjunto cinza elegante com camisa e calça."},
        {"id": 10, "nome": "Calça Marron & Camisa Cinza", "preco": 299.90, "imagem": "Marron_Cinza.jpeg", "descricao": "Look estiloso com camisa marrom e calça cinza."},
        {"id": 11, "nome": "Calça Jeans & Camisa Xumbo", "preco": 299.90, "imagem": "Conjunto_CMMarronCCCinza.jpeg", "descricao": "Conjunto cinza elegante com camisa e calça."},
        {"id": 12, "nome": "Calça Marron & Camisa Cinza", "preco": 299.90, "imagem": "Conjunto_Jeans_CinzaClaro.jpeg", "descricao": "Look estiloso com camisa marrom e calça cinza."}
    ],
    "Novos Produtos": []  # categoria para produtos adicionados via admin
}

# Função para buscar produto pelo ID (procura em todas categorias)
def buscar_produto_por_id(produto_id):
    for lista in categorias.values():
        for p in lista:
            if p["id"] == produto_id:
                return p
    return None

# Função para gerar novo ID incremental
def gerar_novo_id():
    todos_ids = [p["id"] for produtos in categorias.values() for p in produtos]
    return max(todos_ids, default=0) + 1

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['senha'] == SENHA:
            session['admin'] = True
            return redirect(url_for('painel_admin'))
        else:
            flash('Login inválido')
    return render_template('admin_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def painel_admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        arquivo = request.files.get('imagem')
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        descricao = request.form.get('descricao')

        if arquivo and arquivo.filename != '' and nome and preco:
            # Salvar arquivo na pasta correta
            caminho = os.path.join('static', 'img', 'produtos', arquivo.filename)
            arquivo.save(caminho)

            # Gerar um novo ID único (base simples: último ID + 1)
            max_id = max([p["id"] for cat in categorias.values() for p in cat], default=0)
            novo_id = max_id + 1

            # Adicionar produto na categoria "Novos Produtos"
            novo_produto = {
                "id": novo_id,
                "nome": nome,
                "preco": float(preco),
                "imagem": arquivo.filename,
                "descricao": descricao or ""
            }
            categorias["Novos Produtos"].insert(0, novo_produto)  # insere no começo para aparecer primeiro

            flash('Produto adicionado com sucesso!')
        else:
            flash('Preencha todos os campos e envie uma imagem.')

    return render_template('admin.html')


@app.route('/')
def index():
    busca = request.args.get("busca", "").lower()

    categorias_filtradas = {}

    # Se categoria "Novos Produtos" não estiver vazia, ela vai primeiro e com destaque
    if categorias["Novos Produtos"]:
        produtos_filtrados = [p for p in categorias["Novos Produtos"] if busca in p["nome"].lower()]
        if produtos_filtrados:
            categorias_filtradas["⭐ Novos Produtos"] = produtos_filtrados

    # Depois as outras categorias (exceto "Novos Produtos")
    for categoria, produtos in categorias.items():
        if categoria == "Novos Produtos":
            continue
        produtos_filtrados = [p for p in produtos if busca in p["nome"].lower()]
        if produtos_filtrados:
            categorias_filtradas[categoria] = produtos_filtrados

    return render_template("index.html", categorias=categorias_filtradas, busca=busca)

@app.route("/produto/<int:produto_id>")
def detalhes(produto_id):
    produto = buscar_produto_por_id(produto_id)
    if produto:
        return render_template("detalhes.html", produto=produto)
    else:
        return redirect(url_for("index"))
        

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/contato')
def contato():
    return render_template('contato.html')

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port,debug=True)