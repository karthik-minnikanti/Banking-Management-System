from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import mysql.connector
mydb = mysql.connector.connect(
  host="sql2.freesqldatabase.com",
  user="sql2347742",
  password="mQ9!bR4!",
  database="sql2347742"
)
mycursor = mydb.cursor()
app = Flask(__name__)
#app.config['MONGO_DBNAME'] = 'mongologinexample'
#app.config['MONGO_URI'] = 'mongodb+srv://flask123:flask123@flask123-1ik1p.mongodb.net/<dbname>?retryWrites=true&w=majority'
mongo = PyMongo(app)
@app.route('/createCustomer',methods=['POST', 'GET'])
def createCustomer():
    if request.method == 'POST':
        panNumber  = form.request['panNumber']
        mycursor.execute('SELECT * FROM customer WHERE username = %s', (username,))
        account = mycursor.fetchone()
        existing_user = customers.find_one({'panNumber' : request.form['panNumber']})
        if existing_user is None:
            customers.insert({'name' : request.form['customerName'], 'panNumber':request.form['panNumber'],'gender':request.form['gender'],'age':request.form['age']})
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)