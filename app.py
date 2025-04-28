from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
DATABASE="flasktusk.db"

app = Flask(__name__)

@app.route("/")
def top():
    tusk_list = get_db().execute("select id,deadline,body,priority from tusk").fetchall()
    return render_template('index.html',tusk_list=tusk_list)


@app.route("/regist", methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        #画面からの登録情報の取得
        deadline = request.form.get('deadline')
        body = request.form.get('body')
        priority = request.form.get('priority')
        db = get_db()
        db.execute("insert into tusk (deadline,body,priority) values(?,?,?)", [deadline,body,priority])
        db.commit()
        return redirect('/')

    return render_template('regist.html')


@app.route("/<id>/edit",methods = ['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        deadline = request.form.get('deadline')
        body = request.form.get('body')
        priority = request.form.get('priority')
        db = get_db()
        db.execute("update tusk set deadline=?, body=?, priority=? where id=?", [deadline,body,priority,id])
        db.commit()
        return redirect('/')
    
    post = get_db().execute(
        "select id,deadline,body,priority from tusk where id=?",(id,)
    ).fetchone()
    return render_template('edit.html', post=post)


@app.route("/<id>/delete",methods = ['GET', 'POST'])
def delete(id):    
    if request.method == 'POST':
        db = get_db()
        db.execute("delete from tusk where id=?", (id,))
        db.commit()
        return redirect('/')

    post = get_db().execute(
        "select id,deadline,body,priority from tusk where id=?",(id,)
    ).fetchone()
    return render_template('delete.html', post=post)


#database
def connect_db(): #データベースに繋げる
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
def get_db(): #データベースを取得する
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

if __name__ == "__main__":
    app.run(debug=True)