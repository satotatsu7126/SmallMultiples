# -*- coding:utf8 -*-
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='web')

#@app.route('/')         # このウェブサーバの'/'つまり localhost:50625 へのアクセスに対し
#def root():
#  return send_from_directory('.', 'index.html') # '.'つまりカレントディレクトリのindex.htmlを返す

if __name__ == '__main__':
  app.run(port=50918)   # アプリ起動ポート番号
