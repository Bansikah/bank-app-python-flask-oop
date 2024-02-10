from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/deposit', methods=['GET', 'POST'])

def deposit_form():
    try: 
        
        if request.method == 'POST': 
            account_number = request.values.get('account-number')
            deposit_amount = float(request.values.get('deposit_amount'))
            if deposit_amount <= 0 :
                raise ValueError("Invalid Amount.")
            
            updated_balance = update_balance(account_number, deposit_amount)
            if updated_balance is None:
                raise ValueError("Invalid account number.")
            return "Deposit of {}FCFA successfully processed😊👍. <br>Updated balance: {}FCFA".format(deposit_amount, updated_balance)
        return render_template('deposit.html')
    
    except ValueError as ve:
        error_message = f"Error: {ve}"
        return f'<div style="color: red;">{error_message}</div>'
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        return f'<div style="color: red;">{error_message}</div>'

# Function to update balance in the CSV file
def update_balance(account_number, deposit_amount):
    try:
        with open('data.csv', mode='r') as file:
            reader = csv.DictReader(file)
            accounts = list(reader)

        for account in accounts:
            if account['account_number'] == account_number:
                current_balance = float(account['balance'].replace(',', ''))
                new_balance = current_balance + deposit_amount
                account['balance'] = str(new_balance)
                updated_balance = new_balance
                break
            else:
                return None


        with open('data.csv', mode='w', newline='') as file:
            fieldnames = ['account_number', 'balance']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(accounts)
        return updated_balance
    
    except ValueError as ve:
        print(f"Error: {ve}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
         
    
if __name__ == '__main__':
    app.run(debug=True)