from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import bcrypt



app = Flask(__name__)
bcrypt = Bcrypt(app)
# Configure the SQLAlchemy database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use your preferred database UR
db = SQLAlchemy(app)
#db = SQLAlchemy(app, binds={"default": "sqlite:///users.db"})

#app.config['SECRETE_KEY'] = 'secrete'

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
    



class Account(db.Model):                                                       
    account_number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50))
    balance = db.Column(db.Float)
    password = db.Column(db.String(50))
    transactions = db.relationship('Transaction', backref='account', lazy=True)


    def add_transaction(self, amount, description):
        transaction = Transaction(amount=amount, description=description, account_number=self.account_number)
        db.session.add(transaction)
        db.session.commit()



class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), db.ForeignKey('account.account_number'))
    date = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float)
    description = db.Column(db.String(100))


@app.route('/')
def index():
    return render_template('index.html')


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
        user = User(username=username, email=email, phonenumber=phonenumber, password=hashed_password, address=address,country=country, occupation=occupation, account_type=account_type)
        db.session.add(user)
        db.session.commit()
        #return redirect('/login')
    return render_template('home.html', user=user)
    
    
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        sender_account_number = request.form['sender-account-number']
        recipient_account_number = request.form['recipient-account-number']
        recipient_name = request.form['recipient-name']
        amount = float(request.form['amount'])
        password = request.form['password']

        sender = Account.query.filter_by(account_number=sender_account_number).first()
        recipient = Account.query.filter_by(account_number=recipient_account_number, name=recipient_name).first()

        # Validation checks
        error_message = None

        if not sender:
            error_message = "Sender account number is invalid."
        elif not recipient:
            error_message = "Recipient account number or name is invalid."
        elif amount > sender.balance:
            error_message = "Insufficient balance."
        elif password != sender.password:
            error_message = "Incorrect password."

        if error_message:
            return render_template('transfer.html', error_message=error_message, accounts=Account.query.all())

        # Transfer logic
        sender.balance -= amount
        recipient.balance += amount

        # Add transactions to sender and recipient accounts
        sender.add_transaction(-amount, f"Transferred to {recipient_account_number}")
        recipient.add_transaction(amount, f"Received from {sender_account_number}")

        # Save changes to the database
        db.session.commit()

        success_message = f"Successfully transferred {amount} to {recipient_account_number}."

        return render_template('transfer.html', success_message=success_message, accounts=Account.query.all())
    else:
        return render_template('transfer.html', accounts=Account.query.all())


@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        account_number = request.form['account-number']
        account = Account.query.filter_by(account_number=account_number).first()
        if not account:
            error_message = "Invalid account number."
            return render_template('history_form.html', error_message=error_message)

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
        account = Account.query.filter_by(account_number=account_number).first()

        try:
            if account:
                current_balance = account.balance
                if withdraw_amount > current_balance:
                    error_message = "Insufficient balance."
                else:
                    new_balance = current_balance - withdraw_amount
                    account.balance = new_balance
                    db.session.commit()
                    updated_balance = new_balance
                    success_message = f"Withdrawal of {withdraw_amount}FCFA successful😊👍. Updated balance: {updated_balance}FCFA"
            else:
                error_message = "Invalid account number."

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
        account = Account.query.filter_by(account_number=account_number).first()

        try:
            if account:
                if deposit_amount <= 0:
                    error_message = "Amount needs to be greater than 0."
                else:
                    current_balance = account.balance
                    new_balance = current_balance + deposit_amount
                    account.balance = new_balance
                    db.session.commit()
                    updated_balance = new_balance
                    success_message = f"Deposit of {deposit_amount}FCFA successful😊👍. Updated balance: {updated_balance}FCFA"
            else:
                error_message = "Invalid account number."

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('deposit.html', error_message=error_message, success_message=success_message)

#db.create_all()
if __name__ == '__main__':
 with app.app_context():
    db.create_all()
    app.run(debug=True)

