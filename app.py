from flask import Flask
from flask import render_template,g,redirect,request
import sqlite3
DATABASE="flaskmemo.db"
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user #flask-loginのimportに苦戦　仮想環境のディレクトリ名がおかしかったか、vscodeを閉じてからインストールしなければいけないかも
import os
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24) #24バイトでランダムにシークレットキーを管理して、セッション（通信の始まりから終わり）の暗号化を行う
login_manager = LoginManager() #ログインをインスタンス化することで、ログイン機能を色々持ったインスタンスが作成された
login_manager.init_app(app) #このインスタンス化したマネージャに対して、flaskのアプリケーションを紐づけすることで、flaskアプリ上でログインしているかどうかを確認できる

class User(UserMixin): #このクラスをみてユーザがログインしているかを管理する
    def __init__(self,userid):
        self.id = userid
##ログイン
@login_manager.user_loader #ログインしているセッションの確認
def load_user(userid):
    return User(userid)

@login_manager.unauthorized_handler #ログイン認証されていないとログイン画面にとぶようになっている
def unauthorized():
    return redirect('/login')

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return redirect('/login')

@app.route("/signup",methods=['GET','POST'])
def signup():
    error_message = ''
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        pass_hash = generate_password_hash(password,method = 'pbkdf2:sha256') #sha256だけではエラーがでる、左のような形式で指定する必要がある

        db = get_db()
        user_check = get_db().execute("select userid from user where userid=?",[userid,]).fetchall()
        if not user_check:
            db.execute(
                "insert into user (userid,password) values(?,?)",
                [userid,pass_hash]
            )
            db.commit()
            return redirect('/login')
        else:
            error_message = '入力されたユーザIDはすでに利用されています'

    return render_template('signup.html',error_message=error_message)


@app.route("/login",methods=['GET','POST'])
def login():
    error_message = ''
    userid = ''

    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        #ログインのチェック
        user_data = get_db().execute(
            "select password from user where userid=?",[userid,]
        ).fetchone()
        if user_data is not None:
            if check_password_hash(user_data[0],password):
                user = User(userid)
                login_user(user)
                return redirect('/')
        error_message = '入力されたIDもしくはパスワードが誤っています'

    return render_template('login.html', userid=userid,error_message=error_message)
###
@app.route("/")
@login_required
def top():
    memo_list = get_db().execute("select id,title,body from memo").fetchall()
    return render_template('index.html',memo_list=memo_list)

@app.route("/regist",methods=['GET','POST'])
@login_required
def regist():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        db = get_db()
        db.execute("INSERT INTO memo (title,body) VALUES(?,?)",[title,body])
        db.commit()
        return redirect('/')

    return render_template('regist.html')

@app.route("/<id>/edit",methods=['GET','POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        db = get_db()
        db.execute("UPDATE memo set title=?, body=? where id=?",[title,body,id])
        db.commit()
        return redirect('/')

    post = get_db().execute(
        "select id,title,body from memo where id=?",(id,) #id,の,←でタプルの設定を入れないとエラーになる
    ).fetchone()
    return render_template('edit.html',post=post)

@app.route("/<id>/delete",methods=['GET','POST'])
@login_required
def delete(id):
    if request.method == 'POST':
        db = get_db()
        db.execute("DELETE from memo where id=?",(id,))
        db.commit()
        return redirect('/')

    post = get_db().execute(
        "select id,title,body from memo where id=?",(id,) #id,の,←でタプルの設定を入れないとエラーになる
    ).fetchone()
    return render_template('delete.html',post=post)

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