from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "migalhas_secret"

# A Vercel precisa encontrar o objeto 'app'
# Nota: SQLite na Vercel é READ-ONLY após o deploy. 
# Novos registros (reservas/users) sumirão após alguns minutos devido à natureza serverless.

def get_db_connection():
    # Caminho absoluto para evitar erro de 'file not found' no servidor
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "dados.db")
    conn = sqlite3.connect(db_path)
    return conn

# HOME
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("home.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", erro="Login inválido")
    return render_template("login.html")

# REGISTO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
        except:
            return render_template("register.html", erro="Utilizador já existe")
        finally:
            conn.close()
        return redirect("/login")
    return render_template("register.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

produtos = {
    1: {"nome":"Caixa Surpresa do Dia", "imagem":"https://images.unsplash.com/photo-1509440159596-0249088772ff?w=570"},
    2: {"nome":"Box de pastéis", "imagem":"https://curtamais.com.br/brasilia/wp-content/uploads/sites/3/2017/03/4fccc8ca30a27bccce6af4a4119c8cb4-1024x640.jpg?w=570"},
    3: {"nome":"Pack de Croissants", "imagem":"https://staticcookist.akamaized.net/wp-content/uploads/sites/22/2020/06/Croissant23.jpg?w=570"},
    4: {"nome":"Snack box", "imagem":"https://i.pinimg.com/736x/8d/c9/2c/8dc92cb997893a0cc30bf72b2e5ab91d.jpg?w=570"},
    5: {"nome":"Prato de sardinhas", "imagem":"https://www.discoverwalks.com/blog/wp-content/uploads/2018/06/top10portuguesedishesyoushouldtry5-1024x649.jpg?w=570"},
    6: {"nome":"Caixa de frutas", "imagem":"https://hortasaudavel.com.br/wp-content/uploads/2023/05/cesta-frutas-1.jpg?w=570"}
}

# FAVORITOS
@app.route("/favorito", methods=["POST"])
def favorito():
    if "user" not in session: return redirect("/")
    produto_id = request.form["produto_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO favoritos (user, produto_id) VALUES (?, ?)", (session["user"], produto_id))
    conn.commit()
    conn.close()
    return redirect("/favoritos")

@app.route("/favoritos")
def favoritos():
    if "user" not in session: return redirect("/")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT produto_id FROM favoritos WHERE user=?", (session["user"],))
    dados = cursor.fetchall()
    conn.close()
    lista_favoritos = [produtos[int(f[0])] for f in dados if int(f[0]) in produtos]
    return render_template("favoritos.html", favoritos=lista_favoritos)

# RESERVAS
@app.route("/reservar", methods=["POST"])
def reservar():
    if "user" not in session: return redirect("/login")
    produto_id = request.form["produto_id"]
    user = session["user"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas WHERE user=? AND produto_id=?", (user, produto_id))
    if cursor.fetchone():
        conn.close()
        return render_template("home.html", erro="Já reservaste este produto!")
    cursor.execute("INSERT INTO reservas (user, produto_id) VALUES (?, ?)", (user, produto_id))
    conn.commit()
    conn.close()
    return redirect("/reservas")

@app.route("/reservas")
def reservas():
    if "user" not in session: return redirect("/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT produto_id FROM reservas WHERE user=?", (session["user"],))
    dados = cursor.fetchall()
    conn.close()
    lista_reservas = [produtos[int(r[0])] for r in dados if int(r[0]) in produtos]
    return render_template("reservas.html", reservas=lista_reservas)

# ALERTAS
@app.route("/alertas")
def alertas():
    if "user" not in session: return redirect("/login")
    return render_template("alertas.html")

# O Vercel ignora o app.run(), mas mantemos para teste local
if __name__ == "__main__":
    app.run(debug=True)
