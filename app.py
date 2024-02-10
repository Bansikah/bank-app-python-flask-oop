from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transfer.db'
db = SQLAlchemy(app)


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



if __name__ == '__main__':
    app.debug = True
    app.run()