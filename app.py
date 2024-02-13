from flask import Flask, render_template, redirect, request
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import bcrypt

develop

app = Flask(__name__)
bcrypt = Bcrypt(app)
# Configure the SQLAlchemy database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use your preferred database UR
#db = SQLAlchemy(app, binds={"default": "sqlite:///users.db"})
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transfer.db'
#app.config['SECRETE_KEY'] = 'secrete'
db_trans = SQLAlchemy(app)
#Creating a class for the users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False)
    phonenumber = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    occupation = db.Column(db.String(80), nullable=False)
    account_type = db.Column(db.String(80), nullable=False)

    #constructor
    def __init__(self, username, email, phonenumber, password, address, country, occupation, account_type):
       self.username = username
       self.email = email
       self.phonenumber = phonenumber
       self.password = password
       self.address = address
       self.country = country
       self.occupation = occupation
       self.account_type = account_type

    def check_password(self,password):
       return bcrypt.checkpw(password.encode('utf-8'),self.password.encode())
    

from flask import Flask, render_template, request
import csv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
db = SQLAlchemy(app)


class Account(db.Model):                                                       
    account_number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50))
    balance = db.Column(db.Float)
    password = db.Column(db.String(50))
    transactions = db.relationship('Transaction', backref='account', lazy=True)



class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), db.ForeignKey('account.account_number'))
    date = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float)
    description = db.Column(db.String(100))


def load_accounts():
    accounts = []
    with open('database.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            accounts.append(row)
    return accounts

@app.route('/')
def index():
    accounts = load_accounts()
    return render_template('freeze.html', accounts=accounts)

@app.route('/freeze', methods=['POST'])
def freeze_account():
    account_number = request.form['account_number']

    with open('database.csv', 'r') as csvfile:
        accounts = list(csv.DictReader(csvfile))
        for account in accounts:
            if account['Account Number'] == account_number:
                account['Status'] = 'Frozen'
        with open('database.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=accounts[0].keys())
            writer.writeheader()
            writer.writerows(accounts)

    return redirect('/')

@app.route('/unfreeze', methods=['POST'])
def unfreeze_account():
    account_number = request.form['account_number']

    with open('database.csv', 'r') as csvfile:
        accounts = list(csv.DictReader(csvfile))
        for account in accounts:
            if account['Account Number'] == account_number:
                account['Status'] = 'Active'
        with open('database.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=accounts[0].keys())
            writer.writeheader()
            writer.writerows(accounts)

    return redirect('/')

@app.route('/search', methods=['POST'])
def search_account():
    search_query = request.form['search_query']
    accounts = load_accounts()
    search_results = []

    for account in accounts:
        if search_query.lower() in account['Account Name'].lower():
            search_results.append(account)

    if len(search_results) == 0:
        return render_template('not_found.html', search_query=search_query)
    else:
        return render_template('search.html', search_results=search_results, search_query=search_query)

    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # User authentication successful
            return render_template('index.html')
        else:
            # User authentication failed
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user = None  # Initialize the user variable

    if request.method == 'POST':
        # handle request
        username = request.form['username']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #new_user = User(username=username, password=hashed_password)
        address = request.form['address']
        country = request.form['country']
        occupation = request.form['occupation']
        account_type = request.form['account_type']
        user = User(username=username, email=email, phonenumber=phonenumber, password=hashed_password, address=address,
                    country=country, occupation=occupation, account_type=account_type)
        db.session.add(user)
        db.session.commit()
        #return redirect('/login')

    return render_template('registration.html', user=user)

@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        account_number = request.form['account-number']

        account = Account.query.filter_by(account_number=account_number).first()
        if not account:
            error_message = "Invalid account number."
            return render_template('history_form.html', error_message=error_message)
          develop

        transactions = Transaction.query.filter_by(account_number=account_number).all()

        return render_template('history.html', account=account, transactions=transactions)
    else:
        return render_template('history_form.html')


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw_form():
    error_message = None
    success_message = None
    updated_balance = None

    if request.method == 'POST':
        account_number = request.form.get('account-number')
        withdraw_amount = float(request.form.get('withdraw-amount'))

        try:
            with open('data.csv', mode='r') as file:
                reader = csv.DictReader(file)
                accounts = list(reader)

            for account in accounts:
                if account['account_number'] == account_number:
                    current_balance = float(account['balance'].replace(',', ''))
                    if withdraw_amount > current_balance:
                        error_message = "Insufficient balance."
                        break

                    new_balance = current_balance - withdraw_amount
                    account['balance'] = str(new_balance)
                    updated_balance = new_balance
                    success_message = f"Withdrawal of {withdraw_amount}FCFA successful😊👍. Updated balance: {updated_balance}FCFA"
                    break
            else:
                error_message = "Invalid account number."

            if not error_message:
                with open('data.csv', mode='w', newline='') as file:
                    fieldnames = ['account_number', 'balance']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(accounts)

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('withdraw.html', error_message=error_message, success_message=success_message)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit_form():
    error_message = None
    success_message = None
    updated_balance = None

    if request.method == 'POST':
        account_number = request.form.get('account-number')
        deposit_amount = float(request.form.get('deposit-amount'))

        try:
            with open('data.csv', mode='r') as file:
                reader = csv.DictReader(file)
                accounts = list(reader)

            for account in accounts:
                if account['account_number'] == account_number:
                    current_balance = float(account['balance'].replace(',', ''))
                    if deposit_amount <= 0:
                        error_message= "Amount needs to be greater than 0."
                        break

                    new_balance = current_balance + deposit_amount
                    account['balance'] = str(new_balance)
                    updated_balance = new_balance
                    success_message = f"Deposit of {deposit_amount}FCFA successful😊👍. Updated balance: {updated_balance}FCFA"
                    break
            else:
                error_message = "Invalid account number."

            if not error_message:
                with open('data.csv', mode='w', newline='') as file:
                    fieldnames = ['account_number', 'balance']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(accounts)

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('deposit.html', error_message=error_message, success_message=success_message)

#db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
 with app.app_context():
    db.create_all()
    app.run(debug=True)
develop
