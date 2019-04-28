from flask import Flask, render_template, request, redirect, flash, session, abort
import datetime
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb+srv://hhsl:As123456@mempedia-ptiit.mongodb.net/test?retryWrites=true')
with client:
    db = client.mempedia
    cats = list(db.mempedia.find())


@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    with client:
        db = client.mempedia
        cats = list(db.mempedia.find())
    return render_template('index.html', cats=cats)


@app.route('/add', methods=['GET'])
def add_form():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add():
    fields = ['name', 'photo', 'description']
    for field in fields:
        if request.form.get(field, '') == '':
            return redirect('/add')
    cat = {
        'owner': session['username'],
        "name": request.form['name'],
        "description": request.form['description'],
        "photo": request.form['photo'],
        "likes": [],
        "comments": []
    }
    db = client.mempedia
    cats = db.mempedia
    postcats = list(cats.find())
    cats.insert_one(cat)
    return redirect('/cats/{0}'.format(len(postcats)-1))


@app.route('/cats/<id>', methods=['GET'])
def details(id):
    with client:
        db = client.mempedia
        cats = list(db.mempedia.find())
    try:
        cat = cats[int(id)-1]
    except IndexError:
        cat = cats[0]
    name = session['username']
    comms = list(db.comments.find())
    ids = cat['comments']
    coms = []
    for comm in comms:
        for idd in ids:
            if comm['_id'] == idd:
                coms.append(comm)
    return render_template('details.html', cat=cat, id=id, user=name, comments=coms)


@app.route('/like/<id>', methods=['GET'])
def like(id):
    with client:
        db = client.mempedia
        cats = db.mempedia
    postcats = list(cats.find())
    cat = postcats[int(id)-1]
    likes = cat['likes']
    if session['username'] in likes:
        return redirect('/cats/{0}'.format(id))
    likes.append(session['username'])
    objid = cat['_id']
    querry = {'_id': objid}
    newvalues = {'$set': {'likes': likes}}
    cats.update_one(querry, newvalues)
    return redirect('/cats/{0}'.format(id))


@app.route('/comment/<id>', methods=['POST'])
def comment(id):
    fields = ['comment']
    for field in fields:
        if request.form.get(field, '') == '':
            return redirect('/cats/{0}'.format(id))
    with client:
        db = client.mempedia
        cats = db.mempedia
        commentys = db.comments
    postcats = list(cats.find())
    try:
        cat = postcats[int(id)-1]
    except IndexError:
        cat = postcats[0]
    comments = cat['comments']
    objid = cat['_id']
    now = datetime.datetime.now()
    now = (str(now)[0:19])
    comment = {'text': request.form['comment'],
                'author': session['username'],
                'date': str(now)}
    commentys.insert_one(comment)
    comment = list(commentys.find())[-1]
    idd = comment['_id']
    querry = {'_id': objid}
    newvalue = {'$push': {'comments': idd}}
    cats.update(querry, newvalue)
    return redirect('/cats/{0}'.format(id))


@app.route('/login', methods=['POST'])
def login():
    with client:
        db = client.mempedia
        cats = list(db.users.find())
    for cat in cats:
        if request.form['username'] == cat['email'] or request.form['username'] == cat['username']:
            if request.form['password'] == cat['password']:
                session['logged_in'] = True
                session['username'] = cat['username']
            else:
                flash('wrong username or password!')
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/registration', methods=['GET'])
def registration_form():
    return render_template('registration.html')


@app.route('/registration', methods=['POST'])
def registration():
    with client:
        db = client.mempedia
        cats = db.users
    fields = ['login', 'email', 'password1', 'password2']
    for field in fields:
        if request.form.get(field, '') == '':
            return redirect('/registration')
        if request.form['password1'] != request.form['password2']:
            return redirect('/registration')
        users = list(cats.find())
        for user in users:
            for key, item in user.items():
                if request.form[field] == item and field != 'password1' and field != 'password2':
                    flash('Имя пользователя или почта уже занято!')
                    return redirect('/registration')
    user = {'email': request.form['email'],
            'username': request.form['login'],
            'password': request.form['password1']}
    cats.insert_one(user)
    return redirect('/')


@app.route('/delcom/<id>/<idd>', methods=['GET'])
def delcom(id, idd):
    with client:
        db = client.mempedia
        comments = db.comments
        comments.delete_one({'_id': ObjectId(idd)})
    return redirect('/cats/{0}'.format(id))


@app.route('/delmeme/<id>')
def delmeme(id):
    with client:
        db = client.mempedia
        memes = db.mempedia
    print(id)
    memes.delete_one({'_id': ObjectId(id)})
    return redirect('/')


app.secret_key = os.urandom(12)
app.run(debug=True, port=8080)
