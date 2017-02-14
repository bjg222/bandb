from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'This is really unique and secret'
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template("main_page.html")