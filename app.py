from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sklearn.cluster import KMeans
import numpy as np

app = Flask(__name__)

# Define the SQLAlchemy model
Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, Sequence('customer_id_seq'), primary_key=True)
    name = Column(String)
    region = Column(String)
    gender = Column(String)
    age = Column(Integer)
    occupation = Column(String)
    income = Column(Integer)
    products_purchased = Column(Integer)
    money_spent = Column(Integer)

# Create the SQLite database in memory (you can change the URL for a persistent database)
engine = create_engine('sqlite:///mydatabase.db', echo=True)  # Use a persistent database
Base.metadata.create_all(engine)

# Drop and recreate the table with the updated structure
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    customers = session.query(Customer).all()
    # Extract features for clustering (income, occupation, and gender)
    X = np.array([[c.income, c.occupation, 1 if c.gender == 'Male' else 0] for c in customers])

    # Apply K-means clustering with 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Add cluster information to the customers
    for customer, cluster in zip(customers, clusters):
        setattr(customer, 'cluster', cluster)

    # Commit the changes
    session.commit()
    return render_template('index.html', customers=customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form['name']
    region = request.form['region']
    gender = request.form['gender']
    age = request.form['age']
    occupation = request.form['occupation']
    income = request.form['income']
    products_purchased = request.form['products_purchased']
    money_spent = request.form['money_spent']

    new_customer = Customer(
        name=name,
        region=region,
        gender=gender,
        age=age,
        occupation=occupation,
        income=income,
        products_purchased=products_purchased,
        money_spent=money_spent
    )

    session.add(new_customer)
    session.commit()
    return redirect(url_for('index'))

@app.route('/update_customer/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    customer = session.query(Customer).filter_by(customer_id=customer_id).first()
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.region = request.form['region']
        customer.gender = request.form['gender']
        customer.age = request.form['age']
        customer.occupation = request.form['occupation']
        customer.income = request.form['income']
        customer.products_purchased = request.form['products_purchased']
        customer.money_spent = request.form['money_spent']
        session.commit()
        return redirect(url_for('index'))
    return render_template('update_customer.html', customer=customer)

@app.route('/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    customer = session.query(Customer).filter_by(customer_id=customer_id).first()
    session.delete(customer)
    session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

