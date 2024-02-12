from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

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



if __name__ == '__main__':
    app.run()