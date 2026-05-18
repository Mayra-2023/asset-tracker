from flask import Flask, render_template, request, Response
import sqlite3
import os
import csv
import io
import zipfile
from werkzeug.utils import secure_filename
from datetime import datetime

# =========================
# APP INIT (TEM DE SER PRIMEIRO)
# =========================
app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "assets.db")

# =========================
# ROUTES (DEPOIS DO app)
# =========================

@app.route("/")
def index():
    return render_template("index.html")
