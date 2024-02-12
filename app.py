from flask import Flask, render_template, redirect, request
import csv

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)