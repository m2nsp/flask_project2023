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

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('hello'))                #이부분 나중에 view_list로 수정필요
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")
def find_user(self, id_, pw_):
    users = self.db.child("user").get()
    target_value=[]
    for res in users.each():
        value = res.val()

        if value['id'] == id_ and value['pw'] == pw_:
            return True
    return False

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('hello'))                    #이부분 나중에 view_list로 수정필요

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

@application.route('/myPage')
def myPage():
    return render_template('myPage.html')

@application.route('/reg_items')
def reg_items():
    return render_template('reg_items.html')

@application.route("/productList")
def productList():
    return render_template("productList.html")

@application.route("/productRegister")
def productRegister():
    return render_template("productRegister.html")

@application.route("/submit_item_post", methods=['GET', 'POST'])
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

        # Pass the data to the template
        return render_template('productSubmitResult.html', data={
            'product_title': product_title,
            'price_method': price_method,
            'product_description': product_description,
            'user_id': user_id,
            'post_date': post_date,
            'transaction': transaction,
            'normal_price': normal_price,
            'auction_end_time': auction_end_time,
            'auction_min_bid': auction_min_bid,
            'auction_max_bid': auction_max_bid
        })

    # Handle the case when the request method is not POST
    return render_template('productSubmitResult.html')


@application.route("/productSubmitResult", methods=['POST'])
def productSubmitResult():
    image_file = request.files["file"]
    image_path = "static/images/{}".format(image_file.filename)
    image_file.save(image_path)

    # Assuming DB is an instance of your DBhandler class
    DB.insert_item(data=request.form, image_path=image_path)

    return render_template("productSubmitResult.html", data=request.form, img_path=image_path)



@application.route("/reviewRegister")
def reviewRegister():
    return render_template("reviewRegister.html")

@application.route("/myReview")
def myReview():
    return render_template("myReview.html")

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page=6
    per_row=3
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("all_items.html", datas=data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(), limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("detail.html", name=name, data=data)

if __name__ == "__main__":
    application.run(host='0.0.0.0')