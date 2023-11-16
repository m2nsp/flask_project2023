from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/", methods=['GET', 'POST'])
def hello():
    return render_template("home.html")

@application.route('/login')
def login():
    return render_template("login.html")

@application.route("/signup")
def signUp():
    return render_template("signUp.html")

@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@application.route("/home")
def home():
    return render_template("home.html")

@application.route("/myPage")
def myPage():
    return render_template("myPage.html")

@application.route('/submit_item_post', methods=['POST'])
def submit_item_post():
    if request.method == 'POST':
        # Process the form data and store it in Firebase
        img = request.files['img']
        name = request.form['name']
        transaction = request.form.get('transaction')
        price_method = request.form['price-method']

        data = {
            'name': name,
            'transaction': transaction,
            'price-method': price_method,
            # Add other form fields as needed
        }

        if price_method == '일반거래':
            data['normal-price'] = request.form['normal-price']
        elif price_method == '경매':
            data['auction-end-time'] = request.form['auction-end-time']
            data['auction-min-bid'] = request.form['auction-min-bid']
            data['auction-max-bid'] = request.form['auction-max-bid']

        data['product-description'] = request.form['product-description']
        data['post-date'] = request.form['post-date']

        # Upload image to Firebase Storage
        img_path = "static/img/{}".format(image_file.filename)
        storage.child(img_path).put(img)
        data['img_path'] = storage.child(img_path).get_url(None)

        # Store data in Firebase Database
        db.child('items').push(data)

        return render_template('productSubmitResult.html', data=data, img_path="static/img/{}".format(image_file.filename))


@application.route("/reviewRegister")
def reviewRegister():
    return render_template("reviewRegister.html")

@application.route("/myReview")
def myReview():
    return render_template("myReview.html")

@application.route("/productSubmitResult", methods=['POST'])
def productSubmitResult():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("productSubmitResult.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0')