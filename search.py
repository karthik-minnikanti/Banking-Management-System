from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb+srv://flask123:flask123@flask123-1ik1p.mongodb.net/<dbname>?retryWrites=true&w=majority'
mongo = PyMongo(app)
@app.route('/SearchCustomer',methods=['POST', 'GET'])
def SearchCustomer():
    if request.method == 'POST':
        customers = mongo.db.customers
        existing_user = customers.find_one({'panNumber' : request.form['panNumber']})
        if existing_user is None:
            return 'No User Found'
        else:
            return existing_user['name']
    return render_template('search.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)