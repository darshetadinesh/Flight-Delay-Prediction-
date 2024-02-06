import numpy as np
import os
from flask import Flask, request, jsonify, render_template
import pickle
import requests
import sqlite3


app = Flask(__name__)
model = pickle.load(open('rfmodel.pkl', 'rb'))
conn=sqlite3.connect("database1.db")
conn.execute("CREATE TABLE IF NOT EXISTS login(email TEXT PRIMARY KEY,password TEXT)")
conn.close()

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        try:
            print("request1")
            fv=[x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email=request.form["email"]
            pswd=request.form["pswd"]
            print("request2")
            conn=sqlite3.connect("database1.db")
            cur=conn.cursor()
            print(email,pswd)
            cur.execute("SELECT password FROM login WHERE email=?;",(str(email),))
            print("select")
            
            result=cur.fetchone()
            cur.execute("SELECT * FROM login")
            print(cur.fetchall())
            print("fetch")
            if result:
                print("login successfully success")
                print(result)
                if result[0]==pswd:
                    flash("login successfully",'success')
                    return redirect('/home')
                else:
                    return render_template("login.html", error="please enter correct password")
                
            else:
                print("register")
                flash("please Register",'danger')
                
                return redirect('/reg')
            
        except Exception as e:
            print(e)
            print('danger-----------------------------------------------------------------')
            return "hello error" 
#    return render_template('login.html')
@app.route('/reg')
def reg():
    return render_template("register.html")

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        try:
            print("request1")
            fv=[x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email=request.form["email"]
            print(request.form["pswd"])
            pswd=request.form["pswd"]
            conn=sqlite3.connect("database1.db")
            print("database")
            cur=conn.cursor()
            print("cursor")
            cur.execute("SELECT * FROM login WHERE email=?;",(str(email),))
            print("fetch")
            result=cur.fetchone()
            if result:
                print("already")
                flash("user already exist,please login",'danger')
                return redirect('/')
            else:
                print("insert")
                cur.execute("INSERT INTO  login(email,password)values(?,?)",(str(email),str(pswd)))
                conn.commit()
                cur.execute("SELECT * FROM login")
                print(cur.fetchall())
                flash("Registered successfully",'success')
                return render_template('login.html')
            
        except Exception as e:
            print(e)
            #flash(e,'danger')
            return "hello error1"
        
            
                #return redirect('/')
   # return render_template('login.html')

@app.route('/')
def home():
    return render_template('mainpage.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    sm=[6,7,8]
    wt=[9,10,11]
    sp=[12,1,2,3]
    fl=[4,5]
    farr= [int(x) for x in request.form.values()]
    if farr[1] in sm:
        farr.append(0)
    elif farr[1] in wt:
        farr.append(1)
    elif farr[1] in sp:
        farr.append(2)
    else:
        farr.append(3)
    final_features=np.array(farr,dtype='int64')
    print(final_features)
    prediction = model.predict([final_features])
    

    output = round(prediction[0])

    if output==0:
        return render_template('mainpage.html', prediction_text='No delay will happen {}'.format(output))
    elif output==1:
        return render_template('mainpage.html', prediction_text='There is a chance to departure delay will happen {}'.format(output))
    elif output==2:
        return render_template('mainpage.html', prediction_text='here is a chance to both departure and arrival delay will happen {}'.format(output))
    elif output==3:
        return render_template('mainpage.html', prediction_text='here is a chance to flight  will diverted {}'.format(output))
    elif output==4:
        return render_template('mainpage.html', prediction_text='here is a chance to cancel the flight {}'.format(output))
    else:
        return render_template('mainpage.html', prediction_text='output {}'.format(output))
@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request'''
    
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])
    output = prediction[0]
    return jsonify(output)

if __name__ == "__main__":
    os.environ.setdefault('FLASK_ENVS', 'development')
    app.run(debug=False)