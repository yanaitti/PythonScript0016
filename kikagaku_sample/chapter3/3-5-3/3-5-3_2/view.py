# coding: utf-8
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    name = 'キカガク'
    return render_template('index.html', name=name)

# メイン関数
if __name__ == '__main__':
    app.run(debug=True)