# Import necessary modules
import bcrypt
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt



app = Flask(__name__)
bcrypt = Bcrypt(app)
# Configure the SQLAlchemy database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use your preferred database UR
#db = SQLAlchemy(app, binds={"default": "sqlite:///users.db"})
db = SQLAlchemy(app)
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
        user = User(username=username, email=email, phonenumber=phonenumber, password=hashed_password, address=address,
                    country=country, occupation=occupation, account_type=account_type)
        db.session.add(user)
        db.session.commit()
        #return redirect('/login')

    return render_template('registration.html', user=user)

#db.create_all()

if __name__ == '__main__':
 with app.app_context():
    db.create_all()
    app.run(debug=True)