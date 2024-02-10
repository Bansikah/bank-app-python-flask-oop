from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/deposit', methods=['GET', 'POST'])
def deposit_form():
    if request.method == 'POST':
        account_number = request.values.get('account-number')
        deposit_amount = float(request.values.get('deposit_amount'))

        updated_balance = update_balance(account_number, deposit_amount)

        return "Deposit of {} successfully processed for account number {}. <br>Updated balance: {}".format(deposit_amount, account_number, updated_balance)

    return render_template('deposit.html')

# Function to update balance in the CSV file
def update_balance(account_number, deposit_amount):
    with open('data.csv', mode='r') as file:
        reader = csv.DictReader(file)
        accounts = list(reader)

    for account in accounts:
        if account['account_number'] == account_number:
            current_balance = float(account['balance'].replace(',', ''))
            new_balance = current_balance + deposit_amount
            account['balance'] = str(new_balance)
            updated_balance = new_balance

    with open('data.csv', mode='w', newline='') as file:
        fieldnames = ['account_number', 'balance']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(accounts)
    return updated_balance
if __name__ == '__main__':
    app.run(debug=True)