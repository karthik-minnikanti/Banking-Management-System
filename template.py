from flask import Flask, render_template, url_for, request, session, redirect
app = Flask(__name__)
@app.route('/createcustomer')
def index():
    return render_template('createcustomer.html')
@app.route('/updateCustomer')
def update():
    return "NO"
    

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)