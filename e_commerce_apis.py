# Importing libraries
from ctypes.wintypes import FLOAT
from re import S
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import sqlalchemy as db
from sqlalchemy.sql import select

# creating a Flask app
app = Flask(__name__)

#-----------------------------------------

# Route to check db connection
@app.route('/connect', methods = ['GET'])
def dbconnect():
    if(request.method == 'GET'):

        try:
            connection = mysql.connector.connect(
                                host='127.0.0.1',
                                user='root',
                                password='root',
                                database='e_commerce_website')
            if connection.is_connected():
                db_Info = connection.get_server_info()
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)
                cursor.close()
                connection.close()
                s = "Connected to MySQL Server version " + db_Info
                return (s)
                
        except Error as e:
            return ("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                return ("MySQL connection is closed")

#-----------------------------------------

# Route to add user to table
@app.route('/adduser', methods = ['POST'])
def adduser():
    if(request.method == 'POST'):
        engine = db.create_engine('mysql://root:root@127.0.0.1/e_commerce_website')
        connection = engine.connect()
        metadata = db.MetaData()
        request_data = request.get_json()
        
        # Table schema
        user = db.Table('user', metadata,
                    db.Column('User_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('Email_id', db.String(255), nullable=False),
                    db.Column('Password', db.String(255), nullable=False),
                    db.Column('Phone', db.String(255), nullable=False)
                )

        # metadata.create_all(engine) #Creates the table

        query = db.insert(user).values(
                    Email_id=request_data['email'],
                    Password=request_data['password'],
                    Phone=request_data['phone'])

        ResultProxy = connection.execute(query)
        print(ResultProxy)
        return ('success')

#-----------------------------------------

# Route to add product to table
@app.route('/addproduct', methods = ['POST'])
def addproduct():
    if(request.method == 'POST'):
        engine = db.create_engine('mysql://root:root@127.0.0.1/e_commerce_website')
        connection = engine.connect()
        metadata = db.MetaData()
        request_data = request.get_json()
        
        # Table schema
        product = db.Table('product', metadata,
                    db.Column('Product_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Manufacturer', db.String(255), nullable=False),
                    db.Column('Inventory', db.Integer(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False)
                )

        query = db.insert(product).values(
                    Product_name=request_data['product_name'],
                    Manufacturer=request_data['manufacturer'],
                    Inventory=request_data['inventory'],
                    Amount=request_data['amount']
                )

        ResultProxy = connection.execute(query)
        print(ResultProxy)
        return ('success')

#-----------------------------------------

# Route to buy item
@app.route('/buy', methods = ['POST'])
def buy():
    if(request.method == 'POST'):
        engine = db.create_engine('mysql://root:root@127.0.0.1/e_commerce_website')
        connection = engine.connect()
        metadata = db.MetaData()
        request_data = request.get_json()
        
        # Table schema
        buy = db.Table('buy', metadata,
                    db.Column('Buy_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('User_id', db.Integer(), db.ForeignKey("user.User_id"), nullable=False),
                    db.Column('Product_id', db.Integer(), db.ForeignKey("product.Product_id"), nullable=False),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Quantity', db.Float(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False),
                    db.Column('Payment_method', db.String(255), nullable=False)
                )
        
        # Table schema
        product = db.Table('product', metadata,
                    db.Column('Product_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Manufacturer', db.String(255), nullable=False),
                    db.Column('Inventory', db.Integer(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False)
                )

        # Query to insert into buy table
        query = db.insert(buy).values(
                    User_id=request_data['user_id'],
                    Product_id=request_data['product_id'],
                    Product_name=request_data['product_name'],
                    Quantity=request_data['quantity'],
                    Amount=request_data['amount'],
                    Payment_method=request_data['payment_method']
                )

        connection.execute(query)

        # Fetching the product inventory details
        product_query = db.select([product]).where(product.columns.Product_id == request_data['product_id'])
        ResultProxy = connection.execute(product_query)
        ResultSet = ResultProxy.fetchall()

        # Updating the product inventory
        update_query = db.update(product).values(Inventory = (ResultSet[0][3] - int(request_data['quantity'])))
        print(ResultSet[0][3] - int(request_data['quantity']))
        update_query = update_query.where(product.columns.Product_id == request_data['product_id'])
        connection.execute(update_query)
        
        return ('success')

#-----------------------------------------

# Route for adding items to cart
@app.route('/addtocart', methods = ['POST'])
def addtocart():
    if(request.method == 'POST'):
        engine = db.create_engine('mysql://root:root@127.0.0.1/e_commerce_website')
        connection = engine.connect()
        metadata = db.MetaData()
        request_data = request.get_json()
        
        # Table schema
        add_to_cart = db.Table('add_to_cart', metadata,
                    db.Column('Cart_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('User_id', db.Integer(), db.ForeignKey("user.User_id"), nullable=False),
                    db.Column('Product_id', db.Integer(), db.ForeignKey("product.Product_id"), nullable=False),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Quantity', db.Float(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False)
                )

        query = db.insert(add_to_cart).values(
                    User_id=request_data['user_id'],
                    Product_id=request_data['product_id'],
                    Product_name=request_data['product_name'],
                    Quantity=request_data['quantity'],
                    Amount=request_data['amount']
                )

        ResultProxy = connection.execute(query)
        print(ResultProxy)
        return ('success')

#-----------------------------------------

# Route for buying products from cart
@app.route('/buyfromcart', methods = ['POST'])
def buyfromcart():
    if(request.method == 'POST'):
        engine = db.create_engine('mysql://root:root@127.0.0.1/e_commerce_website')
        connection = engine.connect()
        metadata = db.MetaData()
        request_data = request.get_json()
        
        # Table schema
        add_to_cart = db.Table('add_to_cart', metadata,
                    db.Column('Cart_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('User_id', db.Integer(), db.ForeignKey("user.User_id"), nullable=False),
                    db.Column('Product_id', db.Integer(), db.ForeignKey("product.Product_id"), nullable=False),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Quantity', db.Float(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False)
                )
        # Table schema
        buy = db.Table('buy', metadata,
                    db.Column('Buy_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('User_id', db.Integer(), db.ForeignKey("user.User_id"), nullable=False),
                    db.Column('Product_id', db.Integer(), db.ForeignKey("product.Product_id"), nullable=False),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Quantity', db.Float(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False),
                    db.Column('Payment_method', db.String(255), nullable=False)
                )
        
        # Table schema
        product = db.Table('product', metadata,
                    db.Column('Product_id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
                    db.Column('Product_name', db.String(255), nullable=False),
                    db.Column('Manufacturer', db.String(255), nullable=False),
                    db.Column('Inventory', db.Integer(), nullable=False),
                    db.Column('Amount', db.Float(), nullable=False)
                )

        
        # Inserting data into buy table
        for prod_items in request_data['products']:
            # Fetching cart details using user id and product id
            query = db.select([add_to_cart]).where(
                                                db.and_(
                                                    add_to_cart.columns.User_id == request_data['user_id'],
                                                    add_to_cart.columns.Product_id == prod_items['id']))
            ResultProxy = connection.execute(query)
            ResultSet = ResultProxy.fetchall()

            for data in ResultSet:
                insert_query = db.insert(buy).values(
                        User_id=data[1],
                        Product_id=prod_items['id'],
                        Product_name=data[3],
                        Quantity=prod_items['quantity'],
                        Amount=data[5],
                        Payment_method=request_data['payment_method']
                )

                connection.execute(insert_query)
        
        # Updating the product inventory
        for prod_items in request_data['products']:
            # Fetching the product inventory details
            product_query = db.select([product]).where(product.columns.Product_id == prod_items['id'])
            ResultProxy = connection.execute(product_query)
            ResultSet = ResultProxy.fetchall()

            # Query for updating the product table
            update_query = db.update(product).values(Inventory = (ResultSet[0][3] - int(prod_items['quantity'])))
            update_query = update_query.where(product.columns.Product_id == prod_items['id'])
            connection.execute(update_query)

        # Deleteing items from cart after inserting in buy table
        for prod_items in request_data['products']:
            delete_query = db.delete(add_to_cart)
            delete_query = delete_query.where(
                                            db.and_(
                                                add_to_cart.columns.User_id == request_data['user_id'],
                                                add_to_cart.columns.Product_id == prod_items['id']))
            connection.execute(delete_query)
        
        return ('success')

#-----------------------------------------

# driver function
if __name__ == '__main__':

	app.run(debug = True)