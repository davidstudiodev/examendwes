from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'shop2025'

client = MongoClient('mongodb://localhost:27017/')
db = client['examendwes']

users = db['users']
products = db['products']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    
    try:
        object_id = ObjectId(user_id)
        user = db.users.find_one({'_id': object_id})

        if user:
            user = User(user['_id'])
    except Exception as e:
        print('Error: ', e)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
         
        email = request.form['email']
        password = request.form['password']
        
        validateUser = db.users.find_one({'email': email})
        
        if validateUser and check_password_hash(validateUser['password'], password):
        
            
            print('Successful login.')
            return redirect(url_for('profile'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
         
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
         
        validateUser = db.users.find_one({'email': email})
        if validateUser:
             print('This users exists.')
             
        db.users.insert_one({'email': email, 'password': password})
        print('Success user register.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)

