


Claim offer


app.py.txt
Document

requirements.txt
Document

runtime.txt
Document
como hospedar esses ficheiros no Render

O botão Summary serve para mostrar um resumo geral de quantos assets foram verificados ou não verificados por cada depósito.

📌 Em outras palavras:
Ele não mostra detalhes individuais — ele mostra estatísticas.

✅ O que exatamente aparece no Summary?
A página /summary mostra algo assim:

Depósito: Xinavane
Total de assets: 120

Verificados (foto recente ≤ 180 dias): 85

Não verificados (foto antiga > 180 dias): 35

Depósito: Mafambisse
Total de assets: 98

Verificados: 70

Não verificados: 28

Depósito: Matola
Total: 40

Verificados: 40

Não verificados: 0

🎯 Para que isso é útil?
Ele responde perguntas como:

✔ "Quantos assets do depósito estão atrasados para atualização?"
✔ "Quantos já foram verificados?"
✔ "Qual depósito está com mais trabalho pendente?"
É especialmente útil para supervisores, auditores ou relatórios internos.

⚠️ Caso não queira esse botão…
Eu posso:

Remover o botão Summary da página principal, ou

Remover completamente a funcionalidade Summary, ou

Modificar para mostrar outra coisa (ex.: listar os assets semestralmente).

Só me diga:
👉 Quer manter, modificar ou remover o Summary?


esta bem, eu quero que me mostre diariamente, ou seja que seja capaz de geria toda a informacao actualme, logo que e inserida.

Perfeito — você quer que o Summary seja dinâmico, atualizado diariamente, ou melhor dizendo:

➡️ Sempre que alguém adicionar um asset, o Summary já mostra automaticamente.
➡️ Sempre que alguém atualizar uma imagem, o Summary reflete isso na hora.
➡️ Sempre que um asset ultrapassa 180 dias, ele aparece automaticamente como “não verificado”.

💡 Boa notícia:
👉 Seu sistema já funciona assim.
A página Summary é 100% dinâmica baseada no banco de dados.

✅ O que acontece automaticamente hoje?
✔ 1. Summary lê o banco de dados diretamente
Ou seja, não precisa atualizar manualmente.

✔ 2. Se alguém adiciona um novo asset → Summary já conta*
Ele aparece no total do depósito na mesma hora.

✔ 3. Se a foto tem 180+ dias → aparece como Não Verificado*
Esse cálculo é feito no momento em que você abre a página.

✔ 4. Se a pessoa atualiza a foto → volta para Verificado*
Porque a data muda.

✔ O que você quer exatamente melhorar?
Você pode escolher uma destas opções:

A — Mostrar um gráfico diário
Ex.: quantos foram adicionados hoje, ontem, semana.

Como isso:

Hoje: 18 assets adicionados  
Ontem: 22  
Últimos 7 dias: 74
B — Mostrar linha do tempo diária
Por exemplo:

Data	Novos Assets	Atualizados
2026-02-10	12	3
2026-02-11	18	1
2026-02-12	7	4
C — Mostrar painel diário na Home
Algo como:

📅 Hoje:

9 assets adicionados

2 atualizações

1 asset expirado

D — Criar nova página chamada /daily
Para consultar atividade diária.

👉 Qual destas opções você quer implementar?
A, B, C ou D?

Ou você quer criar um Summary ainda mais completo, como dashboards estilo Power BI?


B

Perfeito! Vamos implementar a opção B — Linha do Tempo Diária (Daily Timeline).
Isso significa criar uma página onde você vê por data:

Data	Novos Assets	Atualizações (opcional)
2026-02-10	12	3
2026-02-11	18	1
2026-02-12	7	4
Abaixo eu te dou todo o código completo, incluindo:

✅ 1. ALTERAÇÃO NO app.py — Nova rota /daily
Adicione este bloco antes da parte RUN:

# =========================
# DAILY REPORT
# =========================
@app.route("/daily")
def daily():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            DATE(capture_date) AS day,
            COUNT(*) AS total_assets
        FROM assets
        GROUP BY DATE(capture_date)
        ORDER BY DATE(capture_date) DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template("daily.html", rows=rows)
Isso gera:

✔ número de assets por dia
✔ ordenado do mais recente para o mais antigo

✅ 2. Criar arquivo templates/daily.html
Crie um novo arquivo daily.html na pasta templates:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Activity</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

<div class="container">

    <h1>Daily Asset Activity</h1>
    <img src="/static/logo.png" width="120">

    <p style="margin-top:15px;">Summary of assets captured per day.</p>

    <hr style="margin:25px 0;">

    {% if rows %}
        <table class="table">
            <tr>
                <th>Date</th>
                <th>Total Assets Added</th>
            </tr>

            {% for r in rows %}
            <tr>
                <td>{{ r[0] }}</td>
                <td>{{ r[1] }}</td>
            </tr>
            {% endfor %}
        </table>

    {% else %}
        <p>No activity recorded.</p>
    {% endif %}

    <br><br>
    <a href="/" class="btn">Back to Home</a>

</div>

</body>
</html>
✅ 3. (Opcional) Adicionar o botão Daily Activity na Home
Se quiser aparecer junto com os outros:

No index.html, adicione:

<div class="card">
    <h2>Daily Activity</h2>
    <p>See total assets added per day.</p>
    <a href="/daily" class="btn">View Daily</a>
</div>
🎉 PRONTO!
Agora você terá:

📌 Uma página /daily com linha do tempo diária
📌 Sempre atualizada automaticamente
📌 Mostrando total de assets adicionados por dia

❓ Quer que eu adicione também:
✅ Gráfico diário (barras ou linha)?
✅ Mostrar quantos foram atualizados no dia?
✅ Filtrar por depósito?

Diga SIM caso queira melhorar ainda mais!


Quero exportar link da imagem em vez do arquivo, aqui esta o meu app.py peco para retornar pronto para colar: from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
from datetime import datetime

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = os.path.join(BASE_DIR, "assets.db")

# URL DO SERVIDOR (Render, por exemplo)
RENDER_URL = ""


# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# ADD ASSET
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_asset():

    if request.method == "POST":

        asset_id = request.form["asset_id"]
        depot = request.form["depot"]
        status = request.form["status"]
        captured_by = request.form["captured_by"]
        employee_number = request.form["employee_number"]

        image = request.files["image"]
        capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(image.filename)}"

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assets (
                asset_id, depot, status, captured_by, employee_number, image, capture_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, depot, status, captured_by, employee_number, filename, capture_date))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_asset.html")


# =========================
# SEARCH
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    update_required = False

    if request.method == "POST":
        asset_id = request.form["asset_id"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM assets
            WHERE asset_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        asset = cursor.fetchone()
        conn.close()

        if asset:
            capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
            days_difference = (datetime.now() - capture_date).days

            if days_difference >= 180:
                update_required = True

    return render_template("search.html", asset=asset, update_required=update_required)


# =========================
# UPDATES
# =========================

@app.route("/updates")
def updates():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()

    expired_assets = []

    for asset in assets:
        capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
        days_difference = (datetime.now() - capture_date).days

        if days_difference >= 180:
            expired_assets.append(asset)

    return render_template("updates.html", assets=expired_assets)


# =========================
# SUMMARY
# =========================

@app.route("/summary")
def summary():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT depot, asset_id, capture_date FROM assets")
    rows = cursor.fetchall()
    conn.close()

    summary = {}

    for depot, asset_id, capture_date in rows:

        if depot not in summary:
            summary[depot] = {"total": 0, "verificados": 0, "nao_verificados": 0}

        summary[depot]["total"] += 1

        days = (datetime.now() - datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S")).days

        if days <= 180:
            summary[depot]["verificados"] += 1
        else:
            summary[depot]["nao_verificados"] += 1

    return render_template("summary.html", summary=summary)


# =========================
# EXPORT CSV
# =========================

@app.route("/export")
def export():

    filename = "assets_export.csv"
    filepath = os.path.join(BASE_DIR, filename)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Asset ID", "Depot", "Status",
            "Captured By", "Employee No",
            "Image URL", "Capture Date"
        ])

        for r in rows:
            if r[6]:
                if RENDER_URL:
                    image_url = f"{RENDER_URL}/static/uploads/{r[6]}"
                else:
                    image_url = f"/static/uploads/{r[6]}"
            else:
                image_url = ""

            writer.writerow([r[0], r[1], r[2], r[3], r[4], r[5], image_url, r[7]])

    return send_file(filepath, as_attachment=True)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)

Claro! Aqui está seu app.py corrigido, limpo e 100% pronto para colar.
Ele já exporta o LINK da imagem, nunca o arquivo, exatamente como você pediu.
(Não removi nada além do necessário.)

✅ APP.PY – VERSÃO PRONTA PARA COLAR
✔ Exporta apenas link da imagem
✔ Gera URL completa se RENDER_URL estiver preenchido
✔ Gera URL relativa se estiver rodando local

from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
from datetime import datetime

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = os.path.join(BASE_DIR, "assets.db")

# URL DO SERVIDOR (Render)
RENDER_URL = ""   # <- coloque aqui ex: "https://seuapp.onrender.com"


# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# ADD ASSET
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_asset():

    if request.method == "POST":

        asset_id = request.form["asset_id"]
        depot = request.form["depot"]
        status = request.form["status"]
        captured_by = request.form["captured_by"]
        employee_number = request.form["employee_number"]

        image = request.files["image"]
        capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(image.filename)}"

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assets (
                asset_id, depot, status, captured_by, employee_number, image, capture_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, depot, status, captured_by, employee_number, filename, capture_date))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_asset.html")


# =========================
# SEARCH
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    update_required = False

    if request.method == "POST":
        asset_id = request.form["asset_id"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM assets
            WHERE asset_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        asset = cursor.fetchone()
        conn.close()

        if asset:
            capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
            days_difference = (datetime.now() - capture_date).days

            if days_difference >= 180:
                update_required = True

    return render_template("search.html", asset=asset, update_required=update_required)


# =========================
# UPDATES
# =========================

@app.route("/updates")
def updates():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()

    expired_assets = []

    for asset in assets:
        capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
        days_difference = (datetime.now() - capture_date).days

        if days_difference >= 180:
            expired_assets.append(asset)

    return render_template("updates.html", assets=expired_assets)


# =========================
# SUMMARY
# =========================

@app.route("/summary")
def summary():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT depot, asset_id, capture_date FROM assets")
    rows = cursor.fetchall()
    conn.close()

    summary = {}

    for depot, asset_id, capture_date in rows:

        if depot not in summary:
            summary[depot] = {"total": 0, "verificados": 0, "nao_verificados": 0}

        summary[depot]["total"] += 1

        days = (datetime.now() - datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S")).days

        if days <= 180:
            summary[depot]["verificados"] += 1
        else:
            summary[depot]["nao_verificados"] += 1

    return render_template("summary.html", summary=summary)


# =========================
# EXPORT CSV
# =========================

@app.route("/export")
def export():

    filename = "assets_export.csv"
    filepath = os.path.join(BASE_DIR, filename)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Asset ID", "Depot", "Status",
            "Captured By", "Employee No",
            "Image URL", "Capture Date"
        ])

        for r in rows:

            # LINK DA IMAGEM
            if r[6]:
                if RENDER_URL:
                    image_url = f"{RENDER_URL}/static/uploads/{r[6]}"
                else:
                    image_url = f"/static/uploads/{r[6]}"
            else:
                image_url = ""

            writer.writerow([
                r[0], r[1], r[2], r[3], r[4], r[5],
                image_url, r[7]
            ])

    return send_file(filepath, as_attachment=True)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
🎉 PRONTO!
Agora seu EXPORT CSV sempre gera:

https://seuapp.onrender.com/static/uploads/12345_image.jpg
E nunca o arquivo em si.

❓ Quer que eu também gere:
✅ URL mesmo quando está rodando LOCAL em localhost:5000?
✅ URL encurtada?
✅ Exportar imagem como pré-visualização no Excel (base64)?

Só pedir!


sim

Claro! 🙌
Antes de continuar, preciso que me diga qual das opções você quer ativar no seu sistema de EXPORTAÇÃO.

Aqui estão as 3 possibilidades que mencionei — por favor escolha 1, 2 ou 3:

✅ OPÇÃO 1 — Gerar LINK completo mesmo rodando local
Você quer que o CSV exporte assim mesmo localmente:

http://localhost:5000/static/uploads/123_photo.jpg
✔ Funciona no Excel
✔ Sempre abre a imagem
✔ Mesmo fora do Render

✅ OPÇÃO 2 — Gerar URL encurtada
Transforma isso:

https://seuapp.onrender.com/static/uploads/XZ12.jpg
em algo assim:

https://tinyurl.com/abc123
✔ Fica bonito
✔ Pequeno
⚠️ Requer conexão com internet

✅ OPÇÃO 3 — Exportar imagem “preview” dentro do Excel (BASE64)
Gera no CSV algo assim:

data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ…
E no Excel você insere como "Insert Picture → From Clipboard".

✔ Permite mostrar a miniatura
✔ Não depende de servidor
⚠️ Arquivo CSV fica maior
⚠️ Excel não mostra automaticamente — precisa colar manualmente

❓ Qual opção você quer ativar?
Responda apenas:

➡️ 1 para link local
➡️ 2 para link encurtado
➡️ 3 para exportar imagem em base64

Assim que você escolher, eu retorno o app.py completo e pronto para colar, sem quebrar nada.


Ative a opção exportar imagem em base64

Perfeito! 🔥
Vou agora modificar o EXPORT CSV para que ele exporte a imagem em BASE64, exatamente como pediu.

📌 Resultado:
O arquivo CSV terá uma coluna assim:

data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD…
E no Excel você poderá usar essa string para inserir a imagem manualmente como objeto.

✅ Aqui está o app.py completo e pronto para colar
⚠️ Somente a parte do EXPORT foi alterada — todo o resto permanece igual.

from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
import base64
from datetime import datetime

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = os.path.join(BASE_DIR, "assets.db")

RENDER_URL = ""


# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT,
            depot TEXT,
            status TEXT,
            captured_by TEXT,
            employee_number TEXT,
            image TEXT,
            capture_date TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# ADD ASSET
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_asset():

    if request.method == "POST":

        asset_id = request.form["asset_id"]
        depot = request.form["depot"]
        status = request.form["status"]
        captured_by = request.form["captured_by"]
        employee_number = request.form["employee_number"]

        image = request.files["image"]
        capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(image.filename)}"

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assets (
                asset_id, depot, status, captured_by, employee_number, image, capture_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, depot, status, captured_by, employee_number, filename, capture_date))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_asset.html")


# =========================
# SEARCH
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    asset = None
    update_required = False

    if request.method == "POST":
        asset_id = request.form["asset_id"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM assets
            WHERE asset_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (asset_id,))

        asset = cursor.fetchone()
        conn.close()

        if asset:
            capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
            days_difference = (datetime.now() - capture_date).days

            if days_difference >= 180:
                update_required = True

    return render_template("search.html", asset=asset, update_required=update_required)


# =========================
# UPDATES
# =========================

@app.route("/updates")
def updates():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    conn.close()

    expired_assets = []

    for asset in assets:
        capture_date = datetime.strptime(asset[7], "%Y-%m-%d %H:%M:%S")
        days_difference = (datetime.now() - capture_date).days

        if days_difference >= 180:
            expired_assets.append(asset)

    return render_template("updates.html", assets=expired_assets)


# =========================
# SUMMARY
# =========================

@app.route("/summary")
def summary():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT depot, asset_id, capture_date FROM assets")
    rows = cursor.fetchall()
    conn.close()

    summary = {}

    for depot, asset_id, capture_date in rows:

        if depot not in summary:
            summary[depot] = {"total": 0, "verificados": 0, "nao_verificados": 0}

        summary[depot]["total"] += 1

        days = (datetime.now() - datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S")).days

        if days <= 180:
            summary[depot]["verificados"] += 1
        else:
            summary[depot]["nao_verificados"] += 1

    return render_template("summary.html", summary=summary)


# =========================
# EXPORT CSV (BASE64)
# =========================

@app.route("/export")
def export():

    filename = "assets_export.csv"
    filepath = os.path.join(BASE_DIR, filename)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    rows = cursor.fetchall()
    conn.close()

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Asset ID", "Depot", "Status",
            "Captured By", "Employee No",
            "Image Base64", "Capture Date"
        ])

        for r in rows:
            if r[6]:
                image_path = os.path.join(UPLOAD_FOLDER, r[6])

                if os.path.exists(image_path):
                    with open(image_path, "rb") as img:
                        b64 = base64.b64encode(img.read()).decode("utf-8")
                    image_data = f"data:image/jpeg;base64,{b64}"
                else:
                    image_data = ""
            else:
                image_data = ""

            writer.writerow([r[0], r[1], r[2], r[3], r[4], r[5], image_data, r[7]])

    return send_file(filepath, as_attachment=True)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
🎉 Pronto!
Agora o CSV exporta a imagem inteira em BASE64, ideal para armazenar, mover e reconstruir no Excel.

❓ Quer que eu também:
✔ gere um botão automático no Excel para reconstruir as imagens?
✔ gere uma segunda coluna com thumbnail menor?
✔ compacte a imagem antes de converter (arquivo menor)?

Só pedir!

You're on the free plan
ChatGPT gets less accurate and may forget details in long conversations. Upgrade to chat longer with better memory.

Try Plus free

New chat


