import sqlite3
from datetime import datetime
import os.path as pt
import json

class Database() :
    
    def createUser(self, userId:int) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE id = ?', (userId,))
        existing_user = cursor.fetchone()

        if existing_user is None:
            cursor.execute('INSERT INTO users (id) VALUES (?)', (userId,))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def getAllUsers(self) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = f"SELECT * FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        conn.close()
        
        return users
    
    def getUserNovels(self, userId:int) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = f"SELECT * FROM novels WHERE user_id = {userId} AND image_url <> 0"
        cursor.execute(query)
        novels = cursor.fetchall()
        conn.close()
        
        return novels
    
    def checkGeneratedNovels(self, userId:int) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = f"SELECT * FROM novels WHERE user_id = {userId}"
        cursor.execute(query)
        novel = cursor.fetchone()
        conn.close()
        
        if novel == None:
            return True
        else:
            return False

    def getNovelToGenerate(self) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = "SELECT * FROM novels WHERE is_generated = 0"
        cursor.execute(query)
        novel = cursor.fetchone()
        
        conn.close()
        
        return novel
    
    def getNovelToRead(self, userId:int, novelId:int) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = f"SELECT text,image_url FROM novels WHERE user_id = {userId} AND id = {novelId}"
        cursor.execute(query)
        novel = cursor.fetchone()
        
        conn.close()
        
        return novel
    
    def getNovelToGenerateImage(self) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = f"SELECT text,id FROM novels WHERE image_url = 0 AND is_generated = 1"
        cursor.execute(query)
        novel = cursor.fetchone()
        
        conn.close()
        
        return novel
        
    def getGeneratedNovels(self) :
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        query = "SELECT * FROM novels WHERE is_generated = 1 AND is_send = 0 AND image_url <> 0"
        cursor.execute(query)
        novels = cursor.fetchall()
        
        conn.close()
        
        return novels 

    def createNovel(self,data):
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        userId = data['userId']
        novelData = json.dumps(data)
        
        cursor.execute(f"INSERT INTO novels (user_id,data) VALUES ({userId},'{novelData}')")
        conn.commit()
        
        conn.close()
        
    def updateNovel(self,novelId, text=None, isSend=None, image=None):
        conn = sqlite3.connect(pt.abspath("db/db.db"))
        cursor = conn.cursor()
        
        if text != None :
            query = f"""UPDATE novels SET text = '{text}', is_generated = 1 WHERE id = {novelId}"""
            cursor.execute(query)
            conn.commit()
        elif isSend != None :
            query = f"""UPDATE novels SET is_send = '{isSend}' WHERE id = {novelId}"""
            cursor.execute(query)
            conn.commit()
        elif image != None:
            query = f"""UPDATE novels SET image_url = '{image}' WHERE id = {novelId}"""
            cursor.execute(query)
            conn.commit()
            
        return True

if __name__ == "__main__" : 
    conn = sqlite3.connect(pt.abspath("db/db.db"))
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY NOT NULL
        )"""
    cursor.execute(query)
    query = """CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            text TEXT,
            data TEXT,
            is_generated TEXT DEFAULT 0,
            image_url TEXT DEFAULT 0,
            is_send TEXT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""
    cursor.execute(query)
    query = """CREATE TABLE IF NOT EXISTS public_novels (
            id INTEGER PRIMARY KEY,
            text TEXT,
            data TEXT,
            image_url TEXT DEFAULT 0,
            is_send TEXT DEFAULT 0
        )"""
    cursor.execute(query)
    conn.commit()
    conn.close()
    