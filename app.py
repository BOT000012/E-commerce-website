from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_fallback_secret_key_for_development') # Important for sessions & WTForms
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Route name for the login page
login_manager.login_message_category = 'info' # Flash message category

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one or login.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=False) # 'cosmetics' or 'watches'

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/')
def home():
    products = Product.query.all()
    # For simplicity, we can decide later if "Featured" means all products or a specific subset
    return render_template('E commerce Home Page.html', products=products, title="Featured Products")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') # For redirecting after login if user was trying to access a protected page
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/account")
@login_required # This decorator protects the route
def account():
    return render_template('account.html', title='Account')

@app.route('/category/<string:category_name>')
def show_category(category_name):
    # It's good practice to validate category_name against a list of known categories
    # For now, we'll assume category_name is valid and exists (e.g., 'watches', 'cosmetics', 'perfume')
    # Capitalize category name for display title
    display_title = category_name.capitalize()
    products_in_category = Product.query.filter(Product.category.ilike(category_name)).all()
    return render_template('category_page.html', title=display_title, products=products_in_category, category_name=category_name)

def add_sample_products():
    if not Product.query.first(): # Check if any products exist
        sample_products = [
            Product(name='Luxury Watch Model X', description='A very fine watch.', price=299.99, image_url='https://via.placeholder.com/300x200.png?text=Watch+X', category='watches'),
            Product(name='Elegant Timepiece Y', description='Stylish and elegant.', price=199.50, image_url='https://via.placeholder.com/300x200.png?text=Watch+Y', category='watches'),
            Product(name='Organic Face Cream', description='Natural and soothing.', price=25.00, image_url='https://via.placeholder.com/300x200.png?text=Cream+A', category='cosmetics'),
            Product(name='Silk Lipstick', description='Vibrant and long-lasting.', price=15.99, image_url='https://via.placeholder.com/300x200.png?text=Lipstick+B', category='cosmetics'),
            Product(name='Chronograph Pro', description='For the active individual.', price=450.00, image_url='https://via.placeholder.com/300x200.png?text=Watch+Z', category='watches'),
            Product(name='Revitalizing Serum', description='Youthful glow guaranteed.', price=45.50, image_url='https://via.placeholder.com/300x200.png?text=Serum+C', category='cosmetics'),
            Product(name='Mystic Garden Perfume', description='An enchanting floral scent.', price=75.00, image_url='https://via.placeholder.com/300x200.png?text=Perfume+Mystic', category='perfume'),
            Product(name='Ocean Breeze Eau de Toilette', description='Fresh and invigorating.', price=55.25, image_url='https://via.placeholder.com/300x200.png?text=Perfume+Ocean', category='perfume')
        ]
        db.session.bulk_save_objects(sample_products)
        db.session.commit()
        print("Added sample products to the database.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_sample_products() # Add sample data
    app.run(debug=True)
