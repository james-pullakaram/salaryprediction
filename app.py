from flask import Flask, render_template, request, redirect, session
import sqlite3
import joblib

app = Flask(__name__)
app.secret_key = "mysecretkey"
model = joblib.load("salary_model.pkl")

# Create database table
conn = sqlite3.connect("users.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")
conn.close()


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/home")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/")

    prediction = None

    if request.method == "POST":

        experience = float(request.form["experience"])

        prediction = model.predict([[experience]])

        prediction = round(prediction[0], 2)

    return render_template(
        "home.html",
        prediction=prediction
    )


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=False)