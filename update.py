from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import cgi
form = cgi.FieldStorage()


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb+srv://flask123:flask123@flask123-1ik1p.mongodb.net/<dbname>?retryWrites=true&w=majority'
mongo = PyMongo(app)
@app.route('/updateCustomer',methods=['POST', 'GET'])
def SearchCustomer():
    if request.method == 'POST':
        customers = mongo.db.customers
        existing_user = customers.find_one({'panNumber' : request.form['panNumber']})
        if existing_user is None:
            return 'No User Found'
        else:
            return render_template('update1.html',name=existing_user['name'],age=existing_user['age'])
    return render_template('update.html')
@app.route('/updateCustomer1',methods=['POST', 'GET'])
def updateCustomer():
    name = form.getvalue('name')
    print(request.form['name'])
    if request.method == 'POST':
        customers = mongo.db.customers
        print('successfull')
        return render_template('update1.html')
        '''     existing_user1 = customers.find_one({'panNumber' : existing_user['panNumber']})
        if existing_user is None:
            return 'No User Found'
        else:
            return render_template('update1.html',name=existing_user['name'],age=existing_user['age'])
    return render_template('update.html')  '''
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)