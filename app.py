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

@application.route("/mypage")
def mypage():
    return render_template("mypage.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    if request.method == "POST":
        # Extract form data
        img_file = request.files['img']
        product_title = request.form.get("tit")
        transactions = request.form.getlist("transaction")  # Assuming multiple transactions are possible
        price_method = request.form.get("price-method")
        product_description = request.form.get("product-description")
        user_id = request.form.get("user-id")
        post_date = request.form.get("post-date")

        # Save the uploaded image
        img_filename = request.files["file"]
        img_file.save("static/images/{}".format(img_filename))

        # Handle transactions (checkboxes)
        # You might want to save transactions in a format suitable for your database
        transaction_str = ', '.join(transactions)
        
        if price_method == "일반거래":
            normal_price = request.form.get("normal-price")
            auction_end_time = None
            auction_min_bid = None
            auction_max_bid = None
        elif price_method == "경매":
            normal_price = None
            auction_end_time = request.form.get("auction-end-time")
            auction_min_bid = request.form.get("auction-min-bid")
            auction_max_bid = request.form.get("auction-max-bid")

        # 터미널에 데이터 출력
        print("상품명(글제목):", product_title)
        print("가격방식:", price_method)
        print("거래방식:", transaction)

        if price_method == "일반거래":
            print("판매가:", normal_price)
        elif price_method == "경매":
            print("경매마감일:", auction_end_time)
            print("최저낙찰가:", auction_min_bid)
            print("최고낙찰가:", auction_max_bid)
        
        print("상세설명:", product_description)
        print("글작성날짜:", post_date)

    return "상품이 성공적으로 등록되었습니다."

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