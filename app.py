import hashlib
import time
from flask import Flask, jsonify

app = Flask(__name__)

# =========================
# 🔐 CONFIGURAÇÕES
# =========================
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
CLOUD_NAME = "your_cloud_name"

# =========================
# 🔧 ROTA PARA GERAR SIGNATURE
# =========================
@app.route("/signature", methods=["GET"])
def generate_signature():
    try:
        # ✅ Timestamp obrigatório
        timestamp = int(time.time())

        # ✅ Parâmetros corretos
        params = {
            "folder": "asset_tracker",
            "timestamp": timestamp
        }

        # ✅ Ordenação obrigatória
        sorted_params = "&".join(
            f"{key}={value}" for key, value in sorted(params.items())
        )

        # ✅ String final correta (SEM ERROS)
        string_to_sign = f"{sorted_params}{API_SECRET}"

        # Debug (opcional)
        print("String to sign:", string_to_sign)

        # ✅ Gerar assinatura SHA1
        signature = hashlib.sha1(
            string_to_sign.encode("utf-8")
        ).hexdigest()

        # ✅ Resposta para o frontend
        return jsonify({
            "signature": signature,
            "timestamp": timestamp,
            "api_key": API_KEY,
            "cloud_name": CLOUD_NAME,
            "folder": "asset_tracker"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ✅ ROTA DE TESTE
# =========================
@app.route("/")
def home():
    return "API de assinatura Cloudinary rodando ✅"


# =========================
# ▶️ EXECUÇÃO
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
