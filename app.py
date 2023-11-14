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

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=data.get('pw')
    print("Password:", pw)
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signUp.html")


@application.route("/productList")
def productList():
    return render_template("productList.html")

@application.route("/productRegister")
def productRegister():
    return render_template("productRegister.html")

@application.route("/submit", methods=['POST'])
def submitProduct():
    if request.method == "POST":
        product_title = request.form.get("product-title")
        price_method = request.form.get("price-method")
        product_description = request.form.get("product-description")
        user_id = request.form.get("user-id")
        post_date = request.form.get("post-date")
        transaction = request.form.get("transaction")

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
    return render_template("productSubmitResult.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0')