from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys
from datetime import datetime

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
        return render_template('home.html')                #이부분 나중에 view_list로 수정필요
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
    return render_template('home.html')                    #이부분 나중에 view_list로 수정필요

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
    # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = session.get('id') 
    return render_template('reg_items.html', user_id=user_id)

@application.route("/productList")
def productList():
    return render_template("productList.html")

@application.route("/productRegister")
def productRegister():
    return render_template("productRegister.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'id' in session:
        user_id = session['id']
    else:
        flash("로그인 해야 이용 가능한 기능입니다!")
        return redirect(url_for('login'))    

    image_file = request.files["file"]
    image_file.save("static/img/{}".format(image_file.filename))
    data = request.form.to_dict()
    trade_type = data.get('trade_type')

    if trade_type == 'auction':
        end_date = data.get('end_date')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        data['regular_price'] = None
    else:
        regular_price = data.get('regular_price')
        data['end_date'] = None
        data['min_price'] = None
        data['max_price'] = None

    data['trade_type'] = trade_type
    # data['current_date'] = current_date
    data['user_id'] = user_id
    
    DB.insert_item(data['name'], data, image_file.filename, data['trade_type'], data['end_date'], data['min_price'], data['max_price'], user_id)
    return render_template("productSubmitResult.html", data=data, img_path="static/img/{}".format(image_file.filename))

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
    if data['trade_type'] == 'auction':
        return render_template("detail_general.html", name=name, data=data)
    else:
        return render_template("detail_auction.html", name=name, data=data)


if __name__ == "__main__":
    application.run(host='0.0.0.0')