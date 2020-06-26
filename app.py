from flask import Flask, render_template, url_for, request, session, redirect,Response
import bcrypt
from flask_login import logout_user, LoginManager
import mysql.connector
from datetime import datetime
import io
import xlwt
app = Flask(__name__)
app.secret_key = 'super secret key'
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

dateTimeObj = datetime.utcnow()


#Db connection setup
mydb = mysql.connector.connect(
  host="sql2.freesqldatabase.com",
  user="sql2347742",
  password="mQ9!bR4!",
  database="sql2347742"
)
mycursor = mydb.cursor()

#----------------routes----------------------

#index root
#if username is in session render welcome.html
#else render index page i.e login page
@app.route('/')
def index():
    if 'username' in session:
        return render_template('welcome.html')

    return render_template('index.html',message='')

# login route
#login form validation
#if username is in session then rendor welcome page
#else render index page
#if in form validation then username is searched if present password is checked,
#  if matched then render welcome page else render index page with msg="does match credentials"
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mycursor.execute('SELECT * FROM emp WHERE username = %s ', (username,))
        account = mycursor.fetchone()
        if account:
            if bcrypt.checkpw(password.encode('utf-8'),account[3].encode('utf-8')):
                session['username'] = username
                session['role']=account[4]
                 #session={'username':'imp','role':'customer'}
                return render_template('welcome.html')            
            # Create session data, we can access this data in other routes
            return render_template('index.html',message= "Username and Password do not match")
        else:
            return render_template('index.html',message= "Username and Password do not match")
    if 'username' in session:
        return render_template('welcome.html')
    else:
        return render_template('index.html',message = '')


#admin validation--------------------------------------------------------------------------------------------
@app.route('/registerkey',methods=['POST','GET'])
def keypage():
    return render_template('registerkey.html',message = '')

@app.route('/rootvalidation',methods=['POST','GET'])
def rootvalidation():
    key=request.form['key']
    mycursor.execute('SELECT * FROM seckeys WHERE seckey = %s ', (key,))
    keytup = mycursor.fetchone() 
    print(keytup)
    if keytup:
        session['key']='root'
        return render_template('register.html',message = '')
    else:
        return render_template('registerkey.html',message = 'Invalid key')
                
# Register Routes-------------------------------------------------------------------------------------------
@app.route('/register.html',methods=['POST','GET'])
def registerpage():
    if 'username' in session:
        if(session['username']=='key'):
            return render_template('register.html')
    return render_template('index.html',message='')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'key' not in session:
        return render_template('registerkey.html',message = '')
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
    return render_template('register.html',message="")


# Create Customer Route
#if username is not in session the render index page
# if role is cashier render access denied page
# if all are satisfied then go for post validation and check for pan number length=10 then proceed 
# else render createcustomer page with msg='invalid pan number'
# if pan valid then exectue the queires and display success msg 
@app.route('/createcustomer',methods=['POST', 'GET'])
def createCustomer():
    print(session['role'])
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')

    if session['role']=='cashier':
        return render_template('access.html')
    if request.method == 'POST':
        name = request.form['name']
        pannumber = request.form['pannumber']
        address = request.form['address']
        age = request.form['age']
        gender = request.form['gender']
        message = "Just Created"
        if len(pannumber) == 10:
            mycursor.execute('SELECT * FROM customers WHERE pannumber = %s', (pannumber,))
            account = mycursor.fetchone()
            if not account:
                mycursor.execute('SELECT * FROM customerids' )
                customerid = mycursor.fetchone()
                newcustomerid = customerid[0] + 1
                mycursor.execute("UPDATE customerids SET customerid = %s WHERE customerid = %s" ,(newcustomerid,customerid[0]))
                mydb.commit()
                mycursor.execute('INSERT INTO customers(customerid,customename,pannumber,address,age,gender,message,lastupdated)   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (customerid[0],name,pannumber,address,age,gender,message,dateTimeObj))
                mydb.commit()
                return render_template('createcustomer.html',message='Successfully created')
            return render_template('createcustomer.html',message='PanNumber already Exists')
        return render_template('createcustomer.html',message='PanNumber is invalid')

    return render_template('createcustomer.html',message='')

# search for update
#search either by customerid or by pan number
#if custermerid is found then render updatecustomer page along with customer tuple
#similary for pan, if pan is found then render updatecustomer page along with customer tuple
#if no custer is found either by customerid or by pan number then render searchandupdate page with msg not found
#if customer is found and is in inactive state then render searchandupdate page with msg customer is inactive
@app.route('/searchandupdate',methods=['POST', 'GET'])
def searchcustomer():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        print(customerid)
        pannumber = request.form['pannumber']
        if customerid=='' and pannumber=='':
            return render_template('searchandupdate.html',message='Enter either customer Id or PAN Number')
        else:
            mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
            customer = mycursor.fetchone()
            if customer :
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
                #print('its working')
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
# serach for delete
@app.route('/searchanddelete',methods=['POST', 'GET'])
def searchanddelete():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        session['customerid']=customerid
        # print(customerid)
        pannumber = request.form['pannumber']
        if customerid=='' and pannumber=='':
            return render_template('searchanddelete.html',message='Enter either customer Id or PAN Number')
        else:
            mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
            customer = mycursor.fetchone()
            if customer :
                mycursor.execute('SELECT * FROM customers WHERE customerid = %s', (customerid,))
                customer = mycursor.fetchone()
                if not customer:
                    return render_template('searchanddelete.html',message='No Customer is found')
                else:
                    if customer[3] == '1':
                        session['customerid'] = customerid
                        return render_template('deletecustomer.html',message='',customerid=customerid,address=customer[6],customername=customer[1],age=customer[7])
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
# delete customer

@app.route('/deletecustomer',methods=['POST', 'GET'])
def deletecustomer():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        status = 0
        mycursor.execute('SELECT * FROM accounts WHERE customerid = %s',(session['customerid'],))
        accounts = mycursor.fetchall()
        if accounts:
            if len(accounts)==2:
                if accounts[0][3] == 0 and accounts[1][3] == 0:
                    mycursor.execute("UPDATE customers SET status = %s, lastupdated= %s WHERE customerid = %s" ,(status,dateTimeObj,session['customerid']))
                    mydb.commit()
                    mycursor.execute('UPDATE  customers SET message = %s,lastupdated= %s WHERE customerid = %s',('Customer is set to inactive',dateTimeObj,session['customerid']) )
                    mydb.commit()
                    mycursor.execute('UPDATE accounts SET status = %s WHERE customerid = %s',(status,session['customerid']))
                    mydb.commit()
                    return render_template('searchanddelete.html',message='Successfully Deleted')
                return render_template('searchanddelete.html',message='Please Debit All the amount')
            elif len(accounts)==1:
                if accounts[3] == 0:
                    mycursor.execute("UPDATE customers SET status = %s, lastupdated= %s WHERE customerid = %s" ,(status,dateTimeObj,session['customerid']))
                    mydb.commit()
                    mycursor.execute('UPDATE  customers SET message = %s,lastupdated= %s WHERE customerid = %s',('Customer is set to inactive',dateTimeObj,session['customerid']) )
                    mydb.commit()
                    mycursor.execute('UPDATE accounts SET status = %s WHERE customerid = %s',(status,session['customerid']))
                    mydb.commit()
                    return render_template('searchanddelete.html',message='Successfully Deleted')
                return render_template('searchanddelete.html',message='Please Debit All the amount')
        return render_template('searchanddelete.html',message='Customer Don`t have any accounts')

# update customer
#
@app.route('/updatecustomer',methods=['POST', 'GET'])
def updatecustomer():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    dateTimeObj = datetime.now()
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
            mycursor.execute('UPDATE  customers SET message = %s,lastupdated= %s WHERE customerid = %s',('Updated Name',dateTimeObj,session['customerid']) )
            mydb.commit()

        if age != '':
            mycursor.execute("UPDATE customers SET age = %s WHERE customerid = %s" ,(age,session['customerid']))
            mydb.commit()
            c=c+1
            mycursor.execute('UPDATE  customers SET message = %s,lastupdated= %s WHERE customerid = %s',('Updated age',dateTimeObj,session['customerid']) )
            mydb.commit()
        if address != '':
            mycursor.execute("UPDATE customers SET address = %s WHERE customerid = %s" ,(address,session['customerid']))
            mydb.commit()
            c=c+1
            mycursor.execute('UPDATE  customers SET message = %s,lastupdated= %s WHERE customerid = %s',('Updated address',dateTimeObj,session['customerid']) )
            mydb.commit()
        if c>0:     
            return render_template('searchandupdate.html',message='Successfully updated')
        if c==0:
            return render_template('searchandupdate.html',message='No changes found to update')

# create account for an existing customer
@app.route('/createaccount',methods=['POST', 'GET'])
def createaccount():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        accountype = request.form['type']
        amount = request.form['amount']
        types = ['Savings','Current']
        mycursor.execute('SELECT * from accounts WHERE customerid = %s ',(customerid,))
        type1 = mycursor.fetchall()
        # print(type1)
        if type1:
            if len(type1) == 1:
                if type1[0][2] == accountype:
                    return render_template('createaccount.html',message = 'Customer is already having ' + accountype  + 'account')
            if len(type1) == 2:
                if type1[0][2] == types[0] and type1[1][2] == accountype:
                    return render_template('createaccount.html',message = 'Customer is already having Current account')
                elif type1[1][2] == types[1]:
                    return render_template('createaccount.html',message = 'Customer is already having a Savings account')
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
            ant = accountnumber[0]
            return render_template('createaccount.html',message = 'Successfully created and accountnumber is '+ str(ant))
        return render_template('createaccount.html',message = 'Customer id is inactive')
    return render_template('createaccount.html',message = '')
# delete an account of an Existing Customer
@app.route('/deleteaccount',methods=['POST', 'GET'])
def deleteaccount():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method =='POST':
        accountnumber = request.form['accountnumber']
        mycursor.execute('SELECT * FROM accounts WHERE accountnumber = %s',(accountnumber,) )
        account = mycursor.fetchone()
        if not account:
            return render_template('deleteaccount.html',message = 'NO account found')        
        if account[3] != 0:
            return render_template('deleteaccount.html',message = 'Please Debit amount ' )
        status = 0

        if account[4] == '0':
            return render_template('deleteaccount.html',message = 'Account is already in  inactive state')

        mycursor.execute('UPDATE accounts SET accountstatus = %s WHERE accountnumber = %s',(status,accountnumber))
        mydb.commit()
        
        return render_template('deleteaccount.html',message = 'Successfully deleted')
    return render_template('deleteaccount.html',message = '')
#logout Functionality
# it is working
@app.route('/individualcustomer',methods=['POST', 'GET'])
def individualcustomer():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        mycursor.execute('SELECT * from customers WHERE customerid = %s',(customerid,))
        customer = mycursor.fetchone()
        if not customer:
            return render_template('individualsearch.html',message='No customer id found')
        return render_template('individualcustomerstatus.html',customer = customer)

    return render_template('individualsearch.html',message='')
@app.route('/logout')
def logout():
    if 'username' not in session:
        return render_template('index.html', message= "")
    logout_user()
    session.pop('username',None)
    return render_template('index.html', message= "successfully logged out")
# All Customer Status
#Fetchall the customers from custommers table and render customerstatus page with customer tuple
@app.route('/customersstatus')
def customerstatus():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    mycursor.execute('SELECT * FROM customers')
    customers = mycursor.fetchall()
    # print(customers)
    return render_template('customersstatus.html',customers = customers)

@app.route('/searchforcredit', methods = ['POST','GET'])
def searchfordredit():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        accountid = request.form['accountid']
        session['customerid'] = customerid
        session['accountid'] = accountid
        mycursor.execute('SELECT * from accounts WHERE customerid = %s AND accountnumber = %s ',(customerid,accountid,))
        account = mycursor.fetchone()
        if not account:
            return render_template('creditamount.html',message='No Customer found with that Account Number')        
        mycursor.execute('SELECT * FROM accounts WHERE accountnumber = %s',(session['accountid'],))
        sta = mycursor.fetchone()
        if sta[4] == '0':
            return render_template('creditamount.html',message='Account is inactive')

        session['balance'] = account[3]
        return render_template('creditmoney.html',account = account, customerid = customerid,accountid=accountid)
    return render_template('creditamount.html',message='')
@app.route('/creditamount', methods = ['POST','GET'])
def creditamount():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        amount = request.form['amount']
        mycursor.execute('SELECT * from transactionids')
        transactionid = mycursor.fetchone()
        newatransaction = transactionid[0] + 1
        mycursor.execute("UPDATE transactionids SET transactionid = %s WHERE transactionid = %s" ,(newatransaction,transactionid[0]))
        mydb.commit()
        oldbal = int(session['balance'])
        # print(type(oldbal))
        balance = oldbal + int(amount)
        
        mycursor.execute('UPDATE accounts SET amount = %s WHERE accountnumber = %s',(balance,session['accountid']))
        mydb.commit()
        message = 'credited ' + amount
        msg = message
        mycursor.execute('INSERT INTO transactions(accountnumber,message,transactionid) values(%s,%s,%s)',(session['accountid'],msg,transactionid[0]))
        mydb.commit()
        return render_template('creditamount.html',message='successfully credited and transactionID is ' + str(transactionid[0]) )
@app.route('/searchfordebit',methods = ['POST','GET'])
def searchfordebit():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        accountid = request.form['accountid']
        session['customerid'] = customerid
        session['accountid'] = accountid
        mycursor.execute('SELECT * from accounts WHERE customerid = %s AND accountnumber = %s ',(customerid,accountid,))
        account = mycursor.fetchone()
        mycursor.execute('SELECT * FROM accounts WHERE accountnumber = %s',(session['accountid'],))
        sta = mycursor.fetchone()
        if sta[4] == '0':
            return render_template('creditamount.html',message='Account is inactive')
        if not account:
            return render_template('debitamount.html',message='No customer found')
        session['balance'] = account[3]
        return render_template('debitmoney.html',message= '',account = account[3], customerid = customerid,accountid=accountid)

    return render_template('debitamount.html',message='')
@app.route('/debitamount',methods=['POST','GET'])
def debitamount():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        amount = request.form['amount']
        if int(amount) > session['balance']:
            return render_template('debitmoney.html',message='Enter less Amount',account = session['balance'], customerid = session['customerid'],accountid=session['accountid'])
        mycursor.execute('SELECT * from transactionids')
        transactionid = mycursor.fetchone()
        newatransaction = transactionid[0] + 1
        mycursor.execute("UPDATE transactionids SET transactionid = %s WHERE transactionid = %s" ,(newatransaction,transactionid[0]))
        mydb.commit()
        newamount  = session['balance'] - int(amount)
        mycursor.execute('UPDATE accounts SET amount = %s WHERE accountnumber = %s',(newamount,session['accountid']))
        mydb.commit()
        msg = 'Debited ' + amount
        mycursor.execute('INSERT INTO transactions(accountnumber,message,transactionid) values(%s,%s,%s)',(session['accountid'],msg,transactionid[0]))
        mydb.commit()
        return render_template('debitamount.html',message='Successfully Debited and transaction ID is '+ str(transactionid[0]) )
@app.route('/searchforstatement', methods = ['POST','GET'])
def searchforstatement():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        accountid = request.form['accountid']
        lastten = request.form['lastten']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        # print(fromdate)
        # print(todate)
        if lastten=='lastten':
            mycursor.execute('SELECT * from transactions WHERE accountnumber = %s ORDER BY timeoftransaction DESC LIMIT 10',(accountid,))
            transactions = mycursor.fetchall()
            if not transactions:
                return render_template('searchforstatement.html',message='No transactions found')
            return render_template('renderstatement.html',transactions =transactions )
        if fromdate == '' or todate == '':
            return render_template('searchforstatement.html',message='Please Mention both the Dates')
        elif fromdate>todate:
            return render_template('searchforstatement.html',message='Please mention valid Dates')
        else:
            mycursor.execute("SELECT * FROM transactions WHERE timeoftransaction BETWEEN %s and %s and accountnumber = %s",(fromdate,todate,accountid))
            transactions=mycursor.fetchall()
            if not transactions:
                return render_template('searchforstatement.html',message='No transactions found')
            return render_template('renderstatement.html',transactions =transactions )
    return render_template('searchforstatement.html',message='')
@app.route('/download/report/excel',methods = ['POST','GET'])
def downloadexcel():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        accountid = request.form['accountid']
        lastten = request.form['lastten']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
    if lastten=='lastten':
            mycursor.execute('SELECT * from transactions WHERE accountnumber = %s ORDER BY timeoftransaction DESC LIMIT 10',(accountid,))
            transactions = mycursor.fetchall()
            if not transactions:
                return render_template('searchforstatement.html',message='No transactions found')
            output = io.BytesIO()
            workbook = xlwt.Workbook()
            sh = workbook.add_sheet('Transactions')
            sh.write(0, 0, 'accountnumber')
            sh.write(0, 1, 'Description')
            sh.write(0, 2, 'Transaction Id')
            sh.write(0, 3, 'Time')
            idx = 0
            for row in transactions:
                sh.write(idx+1, 0, int(row[0]))
                sh.write(idx+1, 1, row[1])
                sh.write(idx+1, 2, row[2])
                sh.write(idx+1, 3, str(row[3]))
                idx += 1
            workbook.save(output)
            output.seek(0)
            return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=transactions.xls"})
            # return render_template('renderstatement.html',transactions =transactions )
    if fromdate == '' or todate == '':
        return render_template('searchforstatement.html',message='Please Mention both the Dates')
    elif fromdate>todate:
        return render_template('searchforstatement.html',message='Please mention valid Dates')
    else:
        mycursor.execute("SELECT * FROM transactions WHERE timeoftransaction BETWEEN %s and %s and accountnumber = %s",(fromdate,todate,accountid))
        transactions=mycursor.fetchall()
        print('here comes')
        if not transactions:
            print('here conditon comes')
            return render_template('searchforstatement.html',message='No transactions found')
        output = io.BytesIO()
        workbook = xlwt.Workbook()
        sh = workbook.add_sheet('Transactions')
        sh.write(0, 0, 'accountnumber')
        sh.write(0, 1, 'Description')
        sh.write(0, 2, 'Transaction Id')
        sh.write(0, 3, 'Time')
        idx = 0
        for row in transactions:
            sh.write(idx+1, 0, int(row[0]))
            sh.write(idx+1, 1, row[1])
            sh.write(idx+1, 2, row[2])
            sh.write(idx+1, 3, str(row[3]))
            idx += 1
        workbook.save(output)
        output.seek(0)
        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=transactions.xls"})
# app name 

@app.route('/transfermoney', methods = ['POST','GET'])
def transfermoney():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'customer':
        return render_template('access.html')
    if request.method == 'POST':
        customerid = request.form['customerid']
        debittype = request.form['debit']
        credittype = request.form['credit']
        tramount = request.form['amount']
        if debittype == credittype:
            return render_template('transfermoney.html',message='Account types should not be same')
        mycursor.execute('SELECT * from customers WHERE customerid = %s',(customerid,))
        customer = mycursor.fetchone()
        if not customer:
            return render_template('transfermoney.html',message='No customer Found')
        elif customer[3] == '0':
            session['customerid'] = customerid
            return render_template('transfermoney.html',message='Customer is inActive')
        else:
            mycursor.execute('SELECT * from accounts WHERE customerid = %s',(customerid,))
            accounts = mycursor.fetchall()
            # print('fetched')
            if len(accounts) == 2:
                mycursor.execute('SELECT * from accounts WHERE customerid = %s and accounttype = %s',(customerid,debittype,))
                amount1 = mycursor.fetchone()
                # print(amount1[3])
                # print(tramount)
                # print(type(amount1[3]))
                if int(amount1[3]) < int(tramount):
                     return render_template('transfermoney.html',message= 'Insufficient Funds')
                mycursor.execute('SELECT * from transactionids')
                transactionid = mycursor.fetchone()
                newatransaction = transactionid[0] + 1
                mycursor.execute("UPDATE transactionids SET transactionid = %s WHERE transactionid = %s" ,(newatransaction,transactionid[0]))
                mydb.commit()
                msg = 'OWN Account Transfer '+ str(tramount)                  
                mycursor.execute('INSERT INTO transactions(accountnumber,message,transactionid) values(%s,%s,%s)',(amount1[1],msg,transactionid[0]))
                mydb.commit()
                newamount = int(amount1[3]) - int(tramount)
                mycursor.execute('UPDATE accounts SET amount = %s WHERE accountnumber = %s',(newamount,amount1[1]))
                mydb.commit()
                mycursor.execute('SELECT * from accounts WHERE customerid = %s and accounttype = %s',(customerid,credittype,))
                craccount = mycursor.fetchone()
                cramount = int(tramount)+int(craccount[3])
                mycursor.execute('UPDATE accounts SET amount = %s WHERE accountnumber = %s',(cramount,craccount[1]))
                mydb.commit()
                return render_template('transfermoney.html',message= 'Successfully tranferred' + str(transactionid[0]))
            else:

                return render_template('transfermoney.html',message = 'Customer Dont have two accounts')
    return render_template('transfermoney.html',message = '')
@app.route('/accountsstatus')
def accountstatus():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    if session['role'] == 'cashier':
        return render_template('access.html')
    mycursor.execute('SELECT  * from accounts')
    accounts = mycursor.fetchall()
    return render_template('accountstatus.html',accounts = accounts)
@app.route('/Welcome')
def welcome():
    if 'username' not in  session:
        return render_template('index.html',message = 'Please Log in')
    return render_template('welcome.html')
@app.errorhandler(404) 

# inbuilt function which takes error as parameter 
def not_found(e): 
  
# defining function 
  return render_template('404.html') 
@app.errorhandler(500)
def internal_error(error):

    return render_template('500.html') 

# @app.errorhandler(2055)
# def dbconn_error(e):
#     return render_template('500.html')

# @app.errorhandler(10060)
# def dbconn_timeout(e):
#     return render_template('500.html')


@lm.user_loader
def load_user(user):
    # return User.get(user)
    return ("hi")

if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'the random string'  
    app.run(debug=True)


