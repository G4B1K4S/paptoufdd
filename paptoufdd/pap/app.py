from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "migalhas_secret"


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

        conn = sqlite3.connect("dados.db")
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

        conn = sqlite3.connect("dados.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )

            conn.commit()

        except:
            return render_template("register.html", erro="Utilizador já existe")

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

produtos = {
1: {
"nome":"Caixa Surpresa do Dia",
"imagem":"https://images.unsplash.com/photo-1509440159596-0249088772ff?im=Resize,width=570;"
},

2: {
"nome":"Box de pastéis",
"imagem":"https://curtamais.com.br/brasilia/wp-content/uploads/sites/3/2017/03/4fccc8ca30a27bccce6af4a4119c8cb4-1024x640.jpg?im=Resize,width=570;"
},

3: {
"nome":"Pack de Croissants",
"imagem":"https://staticcookist.akamaized.net/wp-content/uploads/sites/22/2020/06/Croissant23.jpg?im=Resize,width=570;"
},

4: {
"nome":"Snack box",
"imagem":"https://i.pinimg.com/736x/8d/c9/2c/8dc92cb997893a0cc30bf72b2e5ab91d--portuguese.jpg?im=Resize,width=570; "
},

5: {
"nome":"Prato de sardinhas",
"imagem":"https://www.discoverwalks.com/blog/wp-content/uploads/2018/06/top10portuguesedishesyoushouldtry5-1024x649.jpg?im=Resize,width=570; "
},

6: {
"nome":"Caixa de frutas",
"imagem":"https://hortasaudavel.com.br/wp-content/uploads/2023/05/cesta-frutas-1.jpg?im=Resize,width=570; "
}
}


# FAVORITOS
@app.route("/favorito", methods=["POST"])
def favorito():

    if "user" not in session:
        return redirect("/")

    produto_id = request.form["produto_id"]

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO favoritos (user, produto_id) VALUES (?, ?)",
        (session["user"], produto_id)
    )

    conn.commit()
    conn.close()

    return redirect("/favoritos")

@app.route("/favoritos")
def favoritos():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT produto_id FROM favoritos WHERE user=?",
        (session["user"],)
    )

    dados = cursor.fetchall()

    conn.close()

    lista_favoritos = []

    for f in dados:

        produto_id = int(f[0])

        produto = produtos.get(produto_id)

        if produto:

            produto = produtos[produto_id]

            lista_favoritos.append({
                "nome": produto["nome"],
                "imagem": produto["imagem"]
            })

    print(lista_favoritos)
    return render_template("favoritos.html", favoritos=lista_favoritos)


# RESERVAS
@app.route("/reservar", methods=["POST"])
def reservar():
    if "user" not in session:
        return redirect("/login")
    
    produto_id = request.form["produto_id"]
    user = session["user"]
    
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    
    # Verificar se já existe reserva
    cursor.execute(
        "SELECT * FROM reservas WHERE user=? AND produto_id=?",
        (user, produto_id)
    )
    reserva_existente = cursor.fetchone()
    
    if reserva_existente:
        conn.close()
        return render_template("home.html", erro="Já reservaste este produto!")  # ← ADICIONEI O return
    
    # Se não existe reserva, insere
    cursor.execute(
        "INSERT INTO reservas (user, produto_id) VALUES (?, ?)",
        (user, produto_id)
    )
    
    conn.commit()
    conn.close()
    
    return redirect("/reservas")

@app.route("/reservas")
def reservas():

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT produto_id FROM reservas WHERE user=?",
    (session["user"],)
    )

    dados = cursor.fetchall()

    conn.close()

    reservas = []

    for r in dados:

        produto = produtos[int(r[0])]

        reservas.append({
        "nome": produto["nome"],
        "imagem": produto["imagem"]
        })

    return render_template("reservas.html", reservas=reservas)

#cancelar reserva
@app.route("/cancelar_reserva/<int:reserva_id>", methods=["POST"])
def cancelar_reserva(reserva_id):
    # Verificar se o utilizador está autenticado
    if "user" not in session:
        return redirect("/login")
    
    user = session["user"]
    
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    
    # Verificar se a reserva pertence ao utilizador atual (segurança)
    cursor.execute(
        "SELECT * FROM reservas WHERE id=? AND user=?",
        (reserva_id, user)
    )
    reserva = cursor.fetchone()
    
    if reserva is None:
        # Reserva não encontrada ou não pertence ao utilizador
        conn.close()
        return render_template("reservas.html", erro="Reserva não encontrada ou já foi cancelada.")
    
    # Eliminar a reserva
    cursor.execute("DELETE FROM reservas WHERE id=?", (reserva_id,))
    conn.commit()
    conn.close()
    
    # Redirecionar de volta para a página de reservas com mensagem de sucesso
    return render_template("reservas.html", sucesso="Reserva cancelada com sucesso!")

# ALERTAS
@app.route("/alertas")
def alertas():

    if "user" not in session:
        return redirect("/login")

    return render_template("alertas.html")


if __name__ == "__main__":
    app.run(debug=True)

