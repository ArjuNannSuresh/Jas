#!/usr/bin/python3
from flask import Flask,render_template,request
import json
import pymysql
from uuid import uuid4
import datetime
import configparser

app = Flask(__name__,static_url_path='/static')

def database_connection():
    
    config = configparser.RawConfigParser()
    config.read('ConfigFile.properties')
    dbname=config.get('DatabaseSection', 'database.dbname')
    user=config.get('DatabaseSection', 'database.user')
    password=config.get('DatabaseSection', 'database.password')
    db = pymysql.connect(host="localhost",user=user, password=password, db=dbname) 
    return db

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/api/v1/fetch_accounts')
def fect_accounts():
    db= database_connection()  
    cursor = db.cursor()
    sql = "SELECT id FROM wallet"
    cursor.execute(sql)
    results = cursor.fetchall()
    return json.dumps(results)

@app.route('/api/v1/init',methods = ['POST', 'GET'])
def init():
    customed_xid = request.form['customed_xid']
    rand_token = str(uuid4()).replace('-','')
    db= database_connection()  
    cursor = db.cursor()
    print(customed_xid,"-------------------------------",rand_token)
    sql = f'Update wallet set token="{rand_token}" where id= "{customed_xid}"'
    print(sql)
    cursor.execute(sql)
    db.commit()
    token={
  "data": {
    "token": rand_token
  },
  "status": "success"
}
    return json.dumps(token)

@app.route('/api/v1/wallet')
def wallet():
    token=request.headers['token']
    now = datetime.datetime.now()
    now=str(now.strftime("%Y-%m-%d %H:%M:%S"))
    print("_______________",token)
    db= database_connection()  
    cursor = db.cursor()
    sql = f"Update wallet set enable='{now}',status='enabled' where token='{token}'"
    print(sql)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    cursor = db.cursor()
    sql = f"SELECT * FROM wallet where token='{token}'"
    cursor.execute(sql)
    results = cursor.fetchall()
    result={ "data": {},"status": "success"}
    result["data"]=results
    return json.dumps(result)

@app.route('/api/v1/wallet/deposits',methods = ['POST', 'GET'])
def deposit():
    token=request.headers['token']
    deposited_amount = request.form['amount']
    db= database_connection()  
    cursor = db.cursor()
    sql = f"SELECT balance FROM wallet where token='{token}'"
    cursor.execute(sql)
    results = cursor.fetchone()
    cursor.close()
    cursor = db.cursor()
    print(results[0])
    balance=int(results[0])+int(deposited_amount)
    sql = f"Update wallet set balance=balance+{deposited_amount} where token='{token}'"
    print(sql)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    return json.dumps({ "data": {"balance":balance},"status": "success"})

@app.route('/api/v1/wallet/withdrawals',methods = ['POST', 'GET'])
def withdrawals():
    token=request.headers['token']
    withdrawals_amount = request.form['amount']
    db= database_connection()  
    cursor = db.cursor()
    sql = f"SELECT balance FROM wallet where token='{token}'"
    cursor.execute(sql)
    results = cursor.fetchone()
    cursor.close()
    print(results[0])
    if(int(results[0])<int(withdrawals_amount)):
        status="failed"
        data="insufficient funds"
        balance=int(results[0])
    else:
        balance=int(results[0])-int(withdrawals_amount)
        cursor1 = db.cursor()
        sql = f"Update wallet set balance=balance-{withdrawals_amount} where token='{token}'"
        print(sql)
        cursor1.execute(sql)
        db.commit()
        cursor1.close()
        status="success"
        data="done"
    return json.dumps({ "data": {"balance":balance},"status": status})

if __name__ == '__main__':
    app.run()
