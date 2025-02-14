from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
DATABASE="price_tracker.db"

app = Flask(__name__)

@app.route("/")
def top():
    item_list = get_db().execute("select id,name,url,current_price,last_checked from memoregister").fetchall()
    return render_template('index.html',item_list=item_list)

if __name__ == "__main__":
    app.run()

#database
def connect_db(): #データベースに繋げる
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db(): #データベースを取得する
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db