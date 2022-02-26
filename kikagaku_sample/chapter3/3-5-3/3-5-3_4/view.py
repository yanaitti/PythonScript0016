# coding: utf-8
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User

app = Flask(__name__)

# DBとの接続
engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)()

@app.route('/')
def index():
    users = session.query(User).all()
    return render_template('index.html', users=users)

# メイン関数
if __name__ == '__main__':
    app.run(debug=True)