from flask import Flask, request, render_template
import os.path as pt
from db.db import Database
import json
import re

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
    novelJson = json.dumps(novel[0])
    novelInfo = json.loads(novel[0],strict=False)
    
    return render_template(pt.abspath('/novel.html'), text = novelInfo['text'], title = novelInfo['title'],image=novel[1])

@app.route('/save_data', methods=['POST'])
def save_data():
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
        "childAge" : childAge
    }
    db = Database()
    db.createNovel(data=model)

    return render_template(pt.abspath('/success.html'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='8080')