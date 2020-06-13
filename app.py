from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
from flask_login import logout_user, LoginManager
import mysql.connector
app = Flask(__name__)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


mydb = mysql.connector.connect(
  host="sql2.freesqldatabase.com",
  user="sql2347742",
  password="mQ9!bR4!",
  database="sql2347742"
)
mycursor = mydb.cursor()


@app.route('/')
def index():
    if 'username' in session:
        return render_template('welcome.html')

    return render_template('index.html',message='')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        mycursor.execute('SELECT * FROM emp WHERE username = %s', (username,))
        account = mycursor.fetchone()
        if account:
            if bcrypt.checkpw(password.encode('utf-8'),account[3].encode('utf-8')):
                session['username'] = username
                session['role']=account[4]
                return render_template('welcome.html')            
            # Create session data, we can access this data in other routes
            return render_template('index.html',message= "Username and Password do not match")
        else:
            return render_template('index.html',message= "Username and Password do not match")
    if session['username']:
        return render_template('welcome.html')
    else:
        return render_template('index.html')



@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        mycursor.execute('SELECT * FROM emp WHERE username = %s', (username,))
        account = mycursor.fetchone()
        if not account: 
            fullname = request.form['fullname']
            role = request.form['role']
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
            mycursor.execute("INSERT INTO emp (name,username,password,role) VALUES (%s,%s,%s,%s)",(fullname,username,hashpass,role))
            mydb.commit()
            session['username'] = request.form['username']
            return redirect(url_for('index'))        
        else:
            return 'User-already exists'        
    return render_template('register.html')

@app.route('/createcustomer',methods=['POST', 'GET'])
def createCustomer():
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        name = request.form['name']
        pannumber = request.form['pannumber']
        address = request.form['address']
        age = request.form['age']
        gender = request.form['gender']
        message = "Just Created"
        mycursor.execute('SELECT * FROM customers WHERE pannumber = %s', (pannumber,))
        account = mycursor.fetchone()
        if not account:
            mycursor.execute('SELECT * FROM customerids' )
            customerid = mycursor.fetchone()
            newcustomerid = customerid[0] + 1
            mycursor.execute("UPDATE customerids SET customerid = %s WHERE customerid = %s" ,(newcustomerid,customerid[0]))
            mydb.commit()
            mycursor.execute('INSERT INTO customers(customerid,customename,pannumber,address,age,gender,message)   VALUES (%s,%s,%s,%s,%s,%s,%s)', (customerid[0],name,pannumber,address,age,gender,message))
            mydb.commit()
            return render_template('createcustomer.html',message='Successfully created')
        return render_template('createcustomer.html',message='PanNumber already Exists')
        

    return render_template('createcustomer.html',message='')
@app.route('/searchandupdate',methods=['POST', 'GET'])
def searchcustomer():
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        print(customerid)
        pannumber = request.form['pannumber']
        if customerid=='' and pannumber=='':
            return render_template('searchandupdate.html',message='Enter either customer Id or PAN Number')
        else:
            if customerid != '' :
                mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
                customer = mycursor.fetchone()
                if not customer:
                    return render_template('searchandupdate.html',message='No Customer is found')
                else:
                    if customer[3] == '1':
                        session['customerid'] = customerid
                        return render_template('updatecustomer.html',message='',customerid=customerid,address= customer[6],customername = customer[1],age=customer[7])
                    return render_template('searchandupdate.html',message='Customer is inactive')
                    
            else:
                print('its working')
                mycursor.execute('SELECT * FROM customers WHERE pannumber = %s', (pannumber,))
                customer = mycursor.fetchone()
                if not customer:
                    return render_template('searchandupdate.html',message='No Customer is found')
                else:
                    if customer[3] == '1':
                        session['customerid'] = customerid
                        return render_template('updatecustomer.html',message='',customerid=customer[0],address= customer[6],customername = customer[1],age=customer[7])
                    return render_template('searchandupdate.html',message='Customer is inactive')
    return render_template('searchandupdate.html',message='')
@app.route('/searchanddelete',methods=['POST', 'GET'])
def searchanddelete():
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        print(customerid)
        pannumber = request.form['pannumber']
        if customerid=='' and pannumber=='':
            return render_template('searchanddelete.html',message='Enter either customer Id or PAN Number')
        else:
            if customerid != '' :
                mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
                customer = mycursor.fetchone()
                if not customer:
                    return render_template('searchanddelete.html',message='No Customer is found')
                else:
                    if customer[3] == '1':
                        session['customerid'] = customerid
                        return render_template('deletecustomer.html',message='',customerid=customerid,address= customer[6],customername = customer[1],age=customer[7])
                    return render_template('searchanddelete.html',message='Customer is inactive')
                    
            else:
                print('its working')
                mycursor.execute('SELECT * FROM customers WHERE pannumber = %s', (pannumber,))
                customer = mycursor.fetchone()
                if not customer:
                    return render_template('searchanddelete.html',message='No Customer is found')
                else:
                    if customer[3] == '1':
                        session['customerid'] = customerid
                        return render_template('updatecustomer.html',message='',customerid=customer[0],address= customer[6],customername = customer[1],age=customer[7])
                    return render_template('searchanddelete.html',message='Customer is inactive')
    return render_template('searchanddelete.html',message='')
@app.route('/deletecustomer',methods=['POST', 'GET'])
def deletecustomer():
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        status = 0
        mycursor.execute("UPDATE customers SET status = %s WHERE customerid = %s" ,(status,session['customerid']))
        mydb.commit()
        return render_template('searchanddelete.html',message='Successfully Deleted')

@app.route('/updatecustomer',methods=['POST', 'GET'])
def updatecustomer():
    if session['role'] == 'cashier':
        return render_template('access.html')
    c = 0
    if request.method == 'POST':
        name= request.form['customername']
        address = request.form['address']
        age = request.form['age']
        if name != '':
            mycursor.execute("UPDATE customers SET customename = %s WHERE customerid = %s" ,(name,session['customerid']))
            mydb.commit()
            c=c+1

        if age != '':
            mycursor.execute("UPDATE customers SET age = %s WHERE customerid = %s" ,(age,session['customerid']))
            mydb.commit()
            c=c+1
        if address != '':
            mycursor.execute("UPDATE customers SET address = %s WHERE customerid = %s" ,(address,session['customerid']))
            mydb.commit()
            c=c+1
        if c>0:
            return render_template('searchandupdate.html',message='Successfully updated')

@app.route('/createaccount',methods=['POST', 'GET'])
def createaccount():
    if session['role'] == 'customer':
        return render_template('access.html')

    if request.method == 'POST':
        customerid = request.form['customerid']
        accountype = request.form['type']
        amount = request.form['amount']
        mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
        customer = mycursor.fetchone()
        if not customer:
            return render_template('createaccount.html',message = 'Customer id is Notfound')
        if customer[3] == '1':
            mycursor.execute('SELECT * FROM accounternumbers' )
            accountnumber = mycursor.fetchone()
            newaccountnumber = accountnumber[0] + 1
            mycursor.execute("UPDATE accounternumbers SET accountnumber = %s WHERE accountnumber = %s" ,(newaccountnumber,accountnumber[0]))
            mydb.commit()
            mycursor.execute("INSERT INTO accounts(customerid,accountnumber,accounttype,amount)   VALUES (%s,%s,%s,%s)", (customerid,accountnumber[0],accountype,amount))
            mydb.commit()
            return render_template('createaccount.html',message = 'Successfully created')
        return render_template('createaccount.html',message = 'Customer id is inactive')
    return render_template('createaccount.html',message = '')
@app.route('/deleteaccount',methods=['POST', 'GET'])
def deleteaccount():
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method =='POST':
        accountnumber = request.form['accountnumber']
        mycursor.execute('SELECT * FROM accounts WHERE accountnumber = %s',(accountnumber,) )
        account = mycursor.fetchone()
        status = 0
        if not account:
            return render_template('deleteaccount.html',message = 'NO account found')
        if account[4] == '0':
            return render_template('deleteaccount.html',message = 'Account is already in  inactive state')

        mycursor.execute('UPDATE accounts SET (accountstatus) = %s WHERE accountnumber = %s',(status,accountnumber))
        mydb.commit()
        return render_template('deleteaccount.html',message = 'Successfully deleted')
    return render_template('deleteaccount.html',message = '')
@app.route('/logout')
def logout():
    if 'username' not in session:
        return render_template('index.html', message= "")
    logout_user()
    session.pop('username',None)
    return render_template('index.html', message= "successfully logged out")

@lm.user_loader
def load_user(user):
    return User.get(user)
    return ("hi")

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)