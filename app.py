from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    return render_template('E commerce Home Page.html', products=products)

def add_sample_products():
    if not Product.query.first(): # Check if any products exist
        sample_products = [
            Product(name='Luxury Watch Model X', description='A very fine watch.', price=299.99, image_url='https://via.placeholder.com/300x200.png?text=Watch+X', category='watches'),
            Product(name='Elegant Timepiece Y', description='Stylish and elegant.', price=199.50, image_url='https://via.placeholder.com/300x200.png?text=Watch+Y', category='watches'),
            Product(name='Organic Face Cream', description='Natural and soothing.', price=25.00, image_url='https://via.placeholder.com/300x200.png?text=Cream+A', category='cosmetics'),
            Product(name='Silk Lipstick', description='Vibrant and long-lasting.', price=15.99, image_url='https://via.placeholder.com/300x200.png?text=Lipstick+B', category='cosmetics'),
            Product(name='Chronograph Pro', description='For the active individual.', price=450.00, image_url='https://via.placeholder.com/300x200.png?text=Watch+Z', category='watches'),
            Product(name='Revitalizing Serum', description='Youthful glow guaranteed.', price=45.50, image_url='https://via.placeholder.com/300x200.png?text=Serum+C', category='cosmetics')
        ]
        db.session.bulk_save_objects(sample_products)
        db.session.commit()
        print("Added sample products to the database.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_sample_products() # Add sample data
    app.run(debug=True)
