from flask import Flask, render_template, request
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


@app.route('/')
def index():
    return render_template('index.html')


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