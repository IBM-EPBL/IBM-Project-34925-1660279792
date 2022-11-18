# main.py
import os
import base64
import io
import math
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import mysql.connector
import hashlib
import datetime
import calendar
import random
from random import randint
from urllib.request import urlopen
import webbrowser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from werkzeug.utils import secure_filename
from PIL import Image

import urllib.request
import urllib.parse


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  charset="utf8",
  database="retailer_inventory"

)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = { 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####
@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""

 
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rt_retailer WHERE uname = %s AND pass = %s AND status=1', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('rt_home'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login.html',msg=msg)

@app.route('/login_cus', methods=['GET', 'POST'])
def login_cus():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rt_customer WHERE uname = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('userhome'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login_cus.html',msg=msg)

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login_admin.html',msg=msg)



@app.route('/reg_retailer', methods=['GET', 'POST'])
def reg_retailer():
    msg=""
    if request.method=='POST':
        name=request.form['name']
        address=request.form['address']
        city=request.form['city']
        mobile=request.form['mobile']
        email=request.form['email']
        uname=request.form['uname']
        pass1=request.form['pass']
        
    
        
        mycursor = mydb.cursor()

        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
    
        mycursor.execute("SELECT count(*) from rt_retailer where uname=%s",(uname,))
        cnt = mycursor.fetchone()[0]

        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM rt_retailer")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
                    
            sql = "INSERT INTO rt_retailer(id,name,address,city,mobile,email,uname,pass,create_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,name,address,city,mobile,email,uname,pass1,rdate)
            mycursor.execute(sql, val)
            mydb.commit()            
            #print(mycursor.rowcount, "Registered Success")
            msg="sucess"
            #if mycursor.rowcount==1:
            return redirect(url_for('login'))
        else:
            msg='Already Exist'
    return render_template('reg_retailer.html',msg=msg)

@app.route('/rt_home', methods=['GET', 'POST'])
def rt_home():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']
    act=request.args.get("act")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer where uname=%s",(uname,))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM rt_product where retailer=%s",(uname,))
    data2 = mycursor.fetchall()

    if act=="del":
        did = request.args.get('did')
        mycursor.execute("SELECT * FROM rt_product where id=%s",(did,))
        dd = mycursor.fetchone()
        os.remove("static/upload/"+dd[6])
        mycursor.execute('delete from rt_product WHERE id = %s', (did, ))
        mydb.commit()
        return redirect(url_for('rt_home'))
    
    return render_template('rt_home.html',data=data,uname=uname,data2=data2,act=act)

@app.route('/rt_sales', methods=['GET', 'POST'])
def rt_sales():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']
    act=request.args.get("act")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer where uname=%s",(uname,))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM rt_cart c,rt_product p where c.pid=p.id && c.status=1 && p.retailer=%s",(uname,))
    data2 = mycursor.fetchall()


    
    return render_template('rt_sales.html',data=data,uname=uname,data2=data2,act=act)

@app.route('/add_cat', methods=['GET', 'POST'])
def add_cat():
    msg=""
    act = request.args.get("act")
    fnn=""
    uname=""
    if 'username' in session:
        uname = session['username']
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer where uname=%s",(uname,))
    data = mycursor.fetchone()
        
    if request.method=='POST':
        category=request.form['category']

        mycursor.execute("SELECT max(id)+1 FROM rt_category")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        
        sql = "INSERT INTO rt_category(id,retailer,category) VALUES (%s, %s, %s)"
        val = (maxid,uname,category)
        mycursor.execute(sql, val)
        mydb.commit()            
        #print(mycursor.rowcount, "Registered Success")
        result="sucess"
        if mycursor.rowcount==1:
            return redirect(url_for('add_cat',act='1'))
        else:
            msg='Already Exist'

    if act=="del":
        did = request.args.get('did')
        mycursor.execute('delete from rt_category WHERE id = %s', (did, ))
        mydb.commit()
        return redirect(url_for('add_cat'))

    
        
    mycursor.execute("SELECT * FROM rt_category where retailer=%s",(uname,))
    data2 = mycursor.fetchall()
    
    return render_template('add_cat.html',msg=msg,uname=uname,data=data,data2=data2,act=act)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    msg=""
    act = request.args.get("act")
    fnn=""
    uname=""
    if 'username' in session:
        uname = session['username']
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer where uname=%s",(uname,))
    data = mycursor.fetchone()
    
    mycursor.execute("SELECT * FROM rt_category where retailer=%s",(uname,))
    data1 = mycursor.fetchall()

    
        
    if request.method=='POST':
        category=request.form['category']
        product=request.form['product']
        price=request.form['price']
        qty=request.form['qty']
        details=request.form['details']
        
    
        file = request.files['file']
        mycursor.execute("SELECT max(id)+1 FROM rt_product")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
            
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            fn=file.filename
            fnn="P"+str(maxid)+fn  
            #fn1 = secure_filename(fn)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fnn))
                
        
        
        sql = "INSERT INTO rt_product(id,retailer,category,product,price,quantity,photo,details) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid,uname,category,product,price,qty,fnn,details)
        mycursor.execute(sql, val)
        mydb.commit()            
        #print(mycursor.rowcount, "Registered Success")
        result="sucess"
        if mycursor.rowcount==1:
            return redirect(url_for('add_product',act='1'))
        else:
            msg='Already Exist'

    

    
        
    mycursor.execute("SELECT * FROM rt_product")
    data2 = mycursor.fetchall()
    
    return render_template('add_product.html',msg=msg,uname=uname,data=data,data1=data1,act=act)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']
    act=request.args.get("act")
    pid=request.args.get("pid")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer where uname=%s",(uname,))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM rt_product where id=%s",(pid,))
    data2 = mycursor.fetchone()

    if request.method=='POST':
        product=request.form['product']
        price=request.form['price']
        qty=request.form['qty']
        details=request.form['details']
        mycursor.execute("update rt_product set product=%s,price=%s,quantity=%s,details=%s where id=%s",(product,price,qty,details,pid))
        mydb.commit()

        mycursor.execute("SELECT * FROM rt_product where id=%s",(pid,))
        dd3 = mycursor.fetchone()
        if dd3[5]>dd3[9]:
            mycursor.execute("update rt_product set status=0 where id=%s",(pid,))
            mydb.commit()
    
        return redirect(url_for('rt_home'))
        
    
    return render_template('edit.html',data=data,uname=uname,data2=data2,act=act)







@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""
    act=request.args.get("act")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rt_retailer")
    data = mycursor.fetchall()

    if act=="yes":
        did=request.args.get("did")
        mycursor.execute("update rt_retailer set status=1 where id=%s",(did,))
        mydb.commit()
        return redirect(url_for("admin"))
    return render_template('admin.html',data=data)

##########################
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


