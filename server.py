from flask import Flask, render_template, request, redirect
import json
import datetime
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://hhsl:As123456@mempedia-ptiit.mongodb.net/test?retryWrites=true')
with client:
    db = client.mempedia
    cats = list(db.mempedia.find())


@app.route('/', methods=['GET'])
def index():
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
        "name": request.form['name'],
        "description": request.form['description'],
        "photo": request.form['photo'],
        "likes": 0,
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
    cat = cats[int(id) - 1]
    return render_template('details.html', cat=cat, id=id)


@app.route('/like/<id>', methods=['GET'])
def like(id):
    with client:
        db = client.mempedia
        cats = db.mempedia
    postcats = list(cats.find())
    cat = postcats[int(id)-1]
    likes = cat['likes']+1
    objid = cat['_id']
    querry = {'_id': objid}
    newvalues = {'$set': {'likes': likes}}
    cats.update_one(querry, newvalues)
    return redirect('/cats/{0}'.format(id))


@app.route('/comment/<id>', methods=['POST'])
def comment(id):
    if request.form['comment'] == '' or request.form['author'] == '':
        redirect('/details/<id>')
    with client:
        db = client.mempedia
        cats = db.mempedia
    postcats = list(cats.find())
    cat = postcats[int(id)-1]
    comments = cat['comments']
    objid = cat['_id']
    now = datetime.datetime.now()
    now = (str(now)[0:19])
    comment = {'text': request.form['comment'],
                'author': request.form['author'],
                'date': str(now)}
    comments.append(comment)
    querry = {'_id': objid}
    newvalue = {'$push': {'comments': comment}}
    cats.update(querry, newvalue)
    return redirect('/cats/{0}'.format(id))


app.run(debug=True, port=8080)
