from flask import Flask, request, render_template
import os.path as pt
from db.db import Database

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(pt.abspath('/form.html'))

@app.route('/novel', methods=['GET'])
def readNovel() :
    db = Database()
    
    userId = request.args.get('userId')
    novelId = request.args.get('novelId')
    novel = db.getNovelToRead(userId=userId, novelId=novelId)
    
    return render_template(pt.abspath('/novel.html'), text = novel[0])

@app.route('/save_data', methods=['POST'])
def saveData():
    userId = request.form['user-id']
    world = request.form['world']
    moral = request.form['moral']
    childName = request.form['child_name']
    childSex = request.form['child_sex']
    childAge = request.form['child_age']
    
    model = {
        "userId" : userId,
        "world" : world,
        "moral" : moral,
        "childName" : childName,
        "childSex" : childSex,
        "childAge" : childAge,
        "author" : "Александр Сергеевич Пушкин"
    }

    db = Database()
    db.createNovel(data=model)

    return 'Отлично, данные записали! Теперь генерируем сказку, это займет около 5 минут. Мы пришлем ее в телеграм, эту страницу можно закрывать'

if __name__ == '__main__':
    app.run(debug=False,port='8000')