
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

from .main import main
from .rsvp import rsvp

app = Flask(__name__)
#TODO: Actual config.  config.py is blank right now, and I'm just manually configging here.  Fix this.
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'bandb-key'

app.register_blueprint(main)
app.register_blueprint(rsvp, url_prefix='/rsvp')






# from flask import Flask, render_template, redirect, request, url_for
# from flask_sqlalchemy import SQLAlchemy
# 
# app = Flask(__name__)
# app.secret_key = 'This is really unique and secret'
# app.config["DEBUG"] = True
# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="bjg222",
#     password="XD5i%z@7Z8LK",
#     hostname="bjg222.mysql.pythonanywhere-services.com",
#     databasename="bjg222$comments",
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
# 
# db = SQLAlchemy(app)
# 
# class Comment(db.Model):
# 
#     __tablename__ = "comments"
# 
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(4096))
# 
# @app.route('/')
# def index():
#     return render_template("parallax.html")
# 
# @app.route('/form', methods=["GET", "POST"])
# def form():
#     if request.method == "GET":
#         return render_template("main_page.html", comments=Comment.query.all())
#     comment = Comment(content=request.form["contents"])
#     db.session.add(comment)
#     db.session.commit()
#     return redirect(url_for("index"))