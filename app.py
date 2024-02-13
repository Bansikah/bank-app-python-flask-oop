from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transfer.db'
db_trans = SQLAlchemy(app)


class Account(db_trans.Model):                                                       
    account_number = db_trans.Column(db_trans.String(10), primary_key=True)
    name = db_trans.Column(db_trans.String(50))
    balance = db_trans.Column(db_trans.Float)
    password = db_trans.Column(db_trans.String(50))
    transactions = db_trans.relationship('Transaction', backref='account', lazy=True)

    def add_transaction(self, amount, description):
        transaction = Transaction(amount=amount, description=description, account_number=self.account_number)
        db_trans.session.add(transaction)
        db_trans.session.commit()


class Transaction(db_trans.Model):
    id = db_trans.Column(db_trans.Integer, primary_key=True)
    account_number = db_trans.Column(db_trans.String(10), db_trans.ForeignKey('account.account_number'))
    date = db_trans.Column(db_trans.DateTime, default=datetime.now)
    amount = db_trans.Column(db_trans.Float)
    description = db_trans.Column(db_trans.String(100))


@app.route('/')
def index():
    return render_template('index.html')


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
        db_trans.session.commit()

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

if __name__ == '__main__':
    app.debug = True
    app.run()