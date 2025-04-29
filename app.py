from flask import Flask, g, render_template, redirect, request
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

@app.route("/")
def top():
    db, cursor = get_db()
    cursor.execute("SELECT id, deadline, body, priority FROM tusk")
    tusk_list = cursor.fetchall()
    return render_template('index.html', tusk_list=tusk_list)

@app.route("/regist", methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        deadline = request.form.get('deadline')
        body = request.form.get('body')
        priority = request.form.get('priority')

        db, cursor = get_db()
        cursor.execute(
            "INSERT INTO tusk (deadline, body, priority) VALUES (%s, %s, %s)",
            (deadline, body, priority)
        )
        db.commit()
        return redirect('/')
    return render_template('regist.html')

@app.route("/<id>/edit", methods=['GET', 'POST'])
def edit(id):
    db, cursor = get_db()
    if request.method == 'POST':
        deadline = request.form.get('deadline')
        body = request.form.get('body')
        priority = request.form.get('priority')
        cursor.execute(
            "UPDATE tusk SET deadline=%s, body=%s, priority=%s WHERE id=%s",
            (deadline, body, priority, id)
        )
        db.commit()
        return redirect('/')

    # GETの場合は対象データを取得して画面に渡す
    cursor.execute("SELECT id, deadline, body, priority FROM tusk WHERE id=%s", (id,))
    post = cursor.fetchone()
    return render_template('edit.html', post=post)

@app.route("/<id>/delete", methods=['GET', 'POST'])
def delete(id):
    db, cursor = get_db()
    if request.method == 'POST':
        cursor.execute("DELETE FROM tusk WHERE id=%s", (id,))
        db.commit()
        return redirect('/')
    
    cursor.execute("SELECT id, deadline, body, priority FROM tusk WHERE id=%s", (id,))
    post = cursor.fetchone()
    return render_template('delete.html', post=post)

def connect_db():
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD")
    )
    return conn

def get_db():
    if 'db' not in g:
        g.db = connect_db()
        g.cursor = g.db.cursor()
    return g.db, g.cursor

if __name__ == "__main__":
    app.run(debug=True)