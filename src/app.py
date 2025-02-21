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
objects = db['objects']

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
        
            user = User(validateUser['_id'])
            login_user(user)
            
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
    
    if request.method == 'POST':
        
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        
        db.objects.insert_one({'name': name, 'price': price, 'description': description})
        
        print('Object add.')
        return redirect(url_for('profile'))
        
    objects = db.objects.find()
    return render_template('profile.html', objects=objects)

@app.route('/delete/<string:id>', methods=['POST'])
def delete(id):
    
    try:
        object_id = ObjectId(id)    
        result = db.objects.delete_one({'_id': object_id})
        
        if result.deleted_count > 0:
            print('Product deleted.')
            return redirect(url_for('profile'))
        
    except Exception as e:
        print('Error: ', e)        

@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    
    object_id = ObjectId(id)
    myobject = db.objects.find_one({'_id': object_id})
    
    try:
        if request.method == 'POST':
                    
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
                    
            update_data = {
                'name': name,
                'price': price,
                'description': description
            }
                    
            result = db.objects.update_one({'_id': object_id}, {'$set': update_data})
            if result.modified_count > 0:
                print('Product update.')
                return redirect(url_for('profile'))
    
    except Exception as e:
        print('Error: ', e)
          
    return render_template('update.html', myobject=myobject)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET'])
def admin():
    
    users = db.users.find()
    
    return render_template('admin.html', users= users)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)

