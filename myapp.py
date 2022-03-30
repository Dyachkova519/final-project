from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pronouncing
import csv
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
from sqlite3 import connect

con = sqlite3.connect('test.db')
cur = con.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    userinput = db.Column(db.Text)
    rhymingline = db.Column(db.Text)
    poemauthor = db.Column(db.Text)
    poemtitle = db.Column(db.Text)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions')
def question_page():
    return render_template(
        'quiz.html'
    )

@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    q3 = request.args.get('rhyme')
    rhymelist = pronouncing.rhymes(q3)
    with open('final-project/poems_collection.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for word in rhymelist:
            for el in reader:
                if word in el['text']:
                    strings = el['text'].split('<br/>')
                    for elem in strings:
                        tokens = word_tokenize(elem)
                        if word in tokens:
                            if word in tokens[-1]:
                                neededstr = elem
                                author = el['author']
                                title = el['title']
                                break
    if 'neededstr' in locals():
        rhymeline = neededstr
        author = author
        title = title
    else:
        rhymeline = False
        author = False
        title = False
    
    userinput = request.args.get('rhyme')
    
    # создаем профиль пользователя
    user = Data(
        userinput=userinput,
        rhymingline=rhymeline,
        poemauthor=author,
        poemtitle=title
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return render_template('stat.html', userword=q3, rhymeline=rhymeline, author=author, title=title)

@app.route('/statistics')
def stats():
    df = pd.read_sql_table('data', 'sqlite:///test.db')
    neededdf = df[df.columns[1:3]].tail(3)
    neededdf.rename(columns={'userinput': 'Введенное слово', 'rhymingline': 'Строка в рифму'}, inplace=True)
    return render_template('statistics.html',  tables=[neededdf.to_html(classes='data')])



if __name__ == '__main__':
    db.create_all()
    app.run()
