from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys
import math
from datetime import datetime

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/", methods=['GET', 'POST'])
def hello():
    items = DB.get_available_items()
    img_paths = [item_data.get("img_path") for item_data in items.values() if item_data.get("img_path")]
    user_id = session.get('id')                                                     #로그인한 id 불러오기
    liked_items = DB.get_liked_items(user_id)                                       #찜한 상품 불러오기
    data = {'items': items, 'img_paths': img_paths, 'liked_items': liked_items}
    return render_template("home.html", data=data, liked_items=liked_items)

@application.route("/base", methods=['GET', 'POST'])
def base():
    return render_template("base.html")


@application.route('/login')
def login():
    return render_template("login.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():                                                               #로그인 로직
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()                    
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('hello'))                
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")
def find_user(self, id_, pw_):                                                  #사용자가 존재하는지 찾는 함수
    users = self.db.child("user").get()                                         #'user' 항목 아래에 사용자의 정보를 저장한다
    target_value=[]
    for res in users.each():
        value = res.val()

        if value['id'] == id_ and value['pw'] == pw_:
            return True
    return False

@application.route("/logout")
def logout_user():
    session.clear()                                 #로그아웃 로직
    return redirect(url_for('hello'))                    

@application.route("/signup")
def signUp():                                       #회원가입
    return render_template("signUp.html")

@application.route("/signup_post", methods=['POST'])
def register_user():                                #회원가입 로직
    data=request.form
    pw=data.get('pw')
    print("Password:", pw)
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()        #패스워드를 해시값으로 처리후 저장
    if DB.insert_user(data, pw_hash):                               #기존에 없는 user일 경우 새로 등록하고 로그인 페이지로 이동
        return render_template("login.html")
    else:
        flash("user id already exist!")                             #기존에 있는 user일 경우 플래시 메세지 반환
        return render_template("signUp.html")

@application.route('/myPage')
def myPage():
    user_id = session.get('id')
    user = DB.get_user_by_id(user_id)  # DB에서 사용자 정보를 가져오는 함수
    
    if user:
        # 해당 사용자의 리뷰 정보 가져오기
        buyer_reviews = DB.get_buyer_reviews_by_user_id(user_id)
        
        # 리뷰 정보에서 평점만 추출하여 숫자로 변환하여 리스트로 저장
        ratings = [float(review['rating']) for review in buyer_reviews if 'rating' in review]
        
        # 리뷰가 있는 경우에만 평균 계산
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        sold_count, bought_count = DB.count_sold_and_bought_items(user_id)
    else:
        average_rating = 0
        sold_count = 0
        bought_count = 0

    return render_template('myPage.html', 
                           average_rating=average_rating, 
                           session=session,
                           sold_count=sold_count,
                           bought_count=bought_count)

@application.route('/myProfile')
def myProfile():
    user_id = session.get('id')
    user = DB.get_user_by_id(user_id)  # DB에서 사용자 정보를 가져오는 함수
    
    if user:
        # 해당 사용자의 리뷰 정보 가져오기
        buyer_reviews = DB.get_buyer_reviews_by_user_id(user_id)
        
        # 리뷰 정보에서 평점만 추출하여 숫자로 변환하여 리스트로 저장
        ratings = [float(review['rating']) for review in buyer_reviews if 'rating' in review]
        
        # 리뷰가 있는 경우에만 평균 계산
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        sold_count, bought_count = DB.count_sold_and_bought_items(user_id)
    else:
        average_rating = 0
        sold_count = 0
        bought_count = 0

    ing_items = DB.get_ing_items_by_user_id(user_id)

    return render_template('myProfile.html', average_rating=average_rating, session=session, ing_items=ing_items, 
                            sold_count=sold_count,
                            bought_count=bought_count,
                            buyer_reviews=buyer_reviews)






@application.route("/productList")
def productList():
    return render_template("productList.html")

# 상품등록 페이지 호출
@application.route('/reg_items')
def reg_items():
    # 결제 등록일과 사용자 아이디를 받아 상품 등록페이지에 전달
    post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    seller_id = session.get('id') 
    return render_template('reg_items.html', seller_id=seller_id, post_date=post_date)

# 상품등록페이지에서 등록시 자동으로 db 등록하기
@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'id' in session:
        seller_id = session['id']
    else:
        flash("로그인 해야 이용 가능한 기능입니다!")
        return redirect(url_for('login'))

    image_file = request.files["file"]
    image_file.save("static/img/{}".format(image_file.filename))
    data = request.form.to_dict()

    # 'transaction' 필드를 항상 리스트로 처리
    data['transaction'] = request.form.getlist('transaction')
    data['post_date'] = post_date
    data['seller_id'] = seller_id

    DB.insert_item(data['name'], data, image_file.filename, seller_id, post_date, data['transaction'])
    item_data = DB.get_item_by_name(str(data['name']))
    return render_template("detail_general.html", name=data['name'], data=item_data, transaction_list=data['transaction'])

# @application.route("/view_detail/<name>/")
# def view_item_detail(name):
#     data = DB.get_item_by_name(str(name))
#     return render_template("detail_general.html", name=name, data=data, transaction_list=data['transaction'])

# 상품 전체 조회 => 거래상태로 sorting
@application.route("/list")
def view_list():
    # 상품 이미지, 등록일, 가격, 거래방식 표시
    post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page = request.args.get("page", 0, type=int)
    item_status = request.args.get("item_status", "all")
    items = DB.get_items_to_list()  # Call the method to get the list of items
    
    if item_status == "available":                                                          #상품의 상태 저장 'available = 등록만 진행된 상태'
        items = [item for item in items if item['item_status'] == "available"]
    elif item_status == "거래완료":
        items = [item for item in items if item['item_status'] == "거래완료"]
        
    per_page = 5
    
    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    data = items[start_idx:end_idx]
    tot_count = len(items)
    item_counts = len(data)
    
    return render_template(
        "all_items.html",
        datas=data,
        page=page,
        page_count=int(math.ceil(tot_count / per_page)),
        all_total = tot_count,
        total=item_counts,
        item_status=item_status,
        post_date=post_date
    )



@application.route("/flip_view")
def flip_view():
    items = DB.get_items()                                                      #플립뷰에 나타낼 상품들 불러오기
    return render_template("flipView.html", items=items)



# 상품 결제 페이지로 넘어감 -> 해결!
@application.route("/purchase_item/<name>/")
def purchase_item(name):                                                        #상품 결제 버튼눌렀을때 결제페이지로 넘어가는 함수
    data=DB.get_item_by_name(str(name))                                         #이름을 통해서 상품정보 가져오는 함수 - 결제 페이지에 해당상품관련 정보 뿌려주기위해 필요함
    return render_template("purchasePage.html", name=name, data=data, transaction_list=data['transaction'])

@application.route('/reg_buy/<string:name>', methods=['POST'])
def reg_buy(name):                                                              #상품 구매시 정보 받아오는 함수
    buyer_id = session.get('id') 

    trans_mode = request.form['transMode']                                      #사용자가 선택한 거래방식
    trans_media = request.form['transMedia']                                    #사용자가 선택한 결제방식

    data = DB.get_item_by_name(name)                                            #이름을 통해서 상품 받아오기

    DB.reg_buy(buyer_id, trans_mode, trans_media, name)

    # 구매 완료 페이지로 이동
    return render_template("detail_purchased.html", name=name, data=data, trans_mode = trans_mode)

# 아이템 상세 정보를 보여주는 엔드포인트. URL에 포함된 상품 이름(name)을 통해 해당 상품의 정보를 가져와 화면에 보여줌.
@application.route("/view_detail/<name>/")
def view_item_detail(name):
    data = DB.get_item_by_name(str(name))   # 상품 이름을 이용하여 데이터베이스(DB)에서 상품 정보를 가져옴    
    comments = DB.get_comments(name)  # 해당 상품에 대한 댓글을 데이터베이스에서 가져옴    
    print(comments)     # 댓글 데이터를 출력 (개발 및 디버깅 용도)    
    if comments is None:    # 댓글이 없는 경우 빈 리스트로 초기화
        comments = []
    # detail_general.html 템플릿에 상품 이름, 상품 정보, 거래 내역, 댓글 데이터를 전달하여 렌더링
    return render_template("detail_general.html", name=name, data=data, transaction_list=data['transaction'], comments=comments)

# 구매한 상품의 상세 정보를 보여주는 엔드포인트. URL에 포함된 상품 이름(name)을 통해 해당 상품의 정보를 가져와 화면에 보여줌.
@application.route("/detail_purchased/<name>/")
def detail_purchased(name):
    data = DB.get_item_by_name(str(name))       # 상품 이름을 이용하여 데이터베이스(DB)에서 상품 정보를 가져옴    
    comments = DB.get_comments(name)        # 해당 상품에 대한 댓글을 데이터베이스에서 가져옴    
    print(comments)     # 댓글 데이터를 출력 (개발 및 디버깅 용도)    
    if comments is None:        # 댓글이 없는 경우 빈 리스트로 초기화
        comments = []
    # detail_purchased.html 템플릿에 상품 이름, 상품 정보, 댓글 데이터를 전달하여 렌더링
    return render_template("detail_purchased.html", name=name, data=data, comments=comments)


@application.route("/complete_transaction/<name>/", methods=['POST'])
def complete_transaction(name):
    # 상품의 거래 상태를 '거래완료'로 변경
    DB.update_item_status(name, '거래완료')
    return redirect(url_for('review_detail', name=name))



# 특정 상품에 대한 좋아요 상태를 확인하는 엔드포인트. URL에 포함된 상품 이름(name)과 세션에 저장된 사용자 ID를 사용하여 해당 사용자의 좋아요 상태를 가져옴.
@application.route("/show_heart/<name>/", methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'], name)     # 사용자의 ID와 상품 이름을 이용하여 데이터베이스(DB)에서 좋아요 상태를 가져옴    
    return jsonify({'my_heart': my_heart})      # 좋아요 상태를 JSON 형식으로 반환

# 특정 상품에 대한 좋아요를 추가하는 엔드포인트. URL에 포함된 상품 이름(name)과 세션에 저장된 사용자 ID를 사용하여 해당 사용자의 좋아요 상태를 'Y'로 업데이트함.
@application.route("/like/<name>/", methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'], 'Y', name)    # 사용자의 ID와 상품 이름을 이용하여 데이터베이스(DB)에서 좋아요 상태를 'Y'로 업데이트    
    return jsonify({'msg': '좋아요 완료!'})     # 업데이트 성공 메시지를 JSON 형식으로 반환

# 특정 상품에 대한 좋아요를 취소하는 엔드포인트. URL에 포함된 상품 이름(name)과 세션에 저장된 사용자 ID를 사용하여 해당 사용자의 좋아요 상태를 'N'으로 업데이트함.
@application.route("/unlike/<name>/", methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'], 'N', name)     # 사용자의 ID와 상품 이름을 이용하여 데이터베이스(DB)에서 좋아요 상태를 'N'으로 업데이트    
    return jsonify({'msg': '좋아요 취소 완료!'})     # 업데이트 성공 메시지를 JSON 형식으로 반환


@application.route("/myLikes")                              #나의 찜 페이지
def my_likes():                             
    if 'id' not in session:                                 #로그인 되어있지 않을 때 로그인 페이지로 돌아감
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))

    user_id = session['id']
    liked_items = DB.get_liked_items(user_id)               #로그인한 사용자의 찜한 상품들을 DB에서 가져옴
    
    return render_template("myLikes.html", liked_items=liked_items)


# 특정 상품에 대한 댓글을 제출하는 엔드포인트. URL에 포함된 상품 이름(name)과 POST 메소드로 전송된 댓글 데이터를 사용하여 해당 상품에 댓글을 추가함.
@application.route("/submit_comment/<name>/", methods=['POST'])
def submit_comment(name):
    comment = request.form  # POST 메소드로 전송된 댓글 데이터를 request.form을 통해 가져옴    
    DB.submit_comment(comment, name)    # 가져온 댓글 데이터와 상품 이름을 이용하여 데이터베이스(DB)에 댓글을 추가함    
    return redirect(url_for("view_item_detail", name=name))     # 댓글 추가 후 상품 상세 페이지로 리다이렉트
    

# 구매한 상품에 대한 댓글을 제출하는 엔드포인트. URL에 포함된 상품 이름(name)과 POST 메소드로 전송된 댓글 데이터를 사용하여 해당 상품에 댓글을 추가함.
@application.route("/submit_comment_purchased/<name>/", methods=['POST'])
def submit_comment_purchased(name):
    id = request.form.get('id')     # POST 메소드로 전송된 댓글 데이터에서 사용자 ID와 댓글 내용을 가져옴
    content = request.form.get('content')
    comment = {'id': id, 'content': content}    # 가져온 사용자 ID와 댓글 내용을 딕셔너리로 구성    
    DB.submit_comment_purchased(comment, name)      # 구매한 상품에 대한 댓글 데이터를 데이터베이스(DB)에 추가함    
    return redirect(url_for("detail_purchased", name=name))     # 댓글 추가 후 구매한 상품 상세 페이지로 리다이렉트

# 사용자가 리뷰를 제출하는 라우트
@application.route("/submit_review", methods=['POST'])
def submit_review():
    # 세션에 사용자 ID가 없으면 로그인이 필요하다는 플래시 메시지를 표시하고 로그인 페이지로 리다이렉션함.
    if 'id' not in session:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))

    # 세션에서 사용자 ID, 상품 이름, 역할을 가져옴.
    user_id = session['id']
    item_name = request.args.get('name')
    role = request.args.get('role')

    # 폼 데이터에서 등급과 리뷰 내용을 가져옴.
    rating = request.form.get('rating')
    review_content = request.form.get('review')

    # 판매자인 경우 판매자 리뷰를, 구매자인 경우 구매자 리뷰를 데이터베이스에 삽입함.
    if role == 'seller':
        DB.insert_seller_review(user_id, item_name, rating, review_content)
    else:
        DB.insert_buyer_review(user_id, item_name, rating, review_content)

    # 리뷰 등록 성공 메시지를 플래시하고 상품 목록 페이지로 리다이렉션함.
    flash("리뷰가 성공적으로 등록되었습니다.")
    return redirect(url_for('view_list'))

# 상품 리뷰 상세 정보 페이지 라우트
@application.route("/reviewDetail/<name>/")
def review_detail(name):
    # 상품, 거래 정보, 판매자 및 구매자 리뷰를 데이터베이스에서 가져옴.
    item_data = DB.get_item_by_name(name)
    trans_info_data = DB.get_trans_info(name)
    seller_review = DB.get_seller_reviews(name)
    buyer_review = DB.get_buyer_reviews(name)

    # 세션에서 사용자 ID를 가져옴.
    user_id = session.get('id') 

    # 사용자가 판매자인지, 구매자인지 확인하고, 상대방의 ID와 역할을 설정함.
    if user_id == item_data['seller_id']:
        trader_id = trans_info_data['buyer_id']
        role = 'seller'
    else:
        trader_id = item_data['seller_id']
        role = 'buyer'

    # 리뷰 상세 정보 페이지를 렌더링함.
    return render_template("reviewDetail.html", trader_id=trader_id, seller_id=item_data['seller_id'], buyer_id=trans_info_data['buyer_id'], img_path=item_data['img_path'], name=name, user_id=user_id, seller_reviews=seller_review, buyer_reviews=buyer_review, price=item_data['price'])

# 상품 리뷰 등록 페이지 라우트
@application.route("/reviewRegister/<name>")
def review_register(name):
    # 상품 및 거래 정보를 데이터베이스에서 가져옴.
    item_data = DB.get_item_by_name(name)
    trans_info_data = DB.get_trans_info(name)
    
    # 세션에서 사용자 ID를 가져옴.
    user_id = session.get('id') 

    # 사용자가 판매자인지, 구매자인지 확인하고, 상대방의 ID와 역할을 설정함.
    if user_id == item_data['seller_id']:
        trader_id = trans_info_data['buyer_id']
        role = 'seller'
    else:
        trader_id = item_data['seller_id']
        role = 'buyer'

    # 리뷰 등록 페이지를 렌더링함.
    return render_template("reviewRegister.html", name=name, trader_id=trader_id, seller_id=item_data['seller_id'], buyer_id=trans_info_data['buyer_id'], img_path=item_data['img_path'], user_id=user_id, price=item_data['price'])

# 사용자의 리뷰 목록 페이지 라우트
@application.route("/myReview/<user_id>")
def my_review(user_id):
    # 로그인되어 있지 않으면 로그인 페이지로 리다이렉션함.
    if 'id' not in session:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))

    # 사용자의 판매자 및 구매자 리뷰를 데이터베이스에서 가져옴.
    seller_reviews = DB.get_seller_reviews_by_user_id(user_id)
    buyer_reviews = DB.get_buyer_reviews_by_user_id(user_id)
    user_reviews = seller_reviews + buyer_reviews

    # 페이지 및 페이지당 리뷰 수를 설정함.
    page = request.args.get("page", 0, type=int)
    per_page = 3

    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    # 현재 페이지에 표시할 리뷰 데이터를 설정함.
    data = user_reviews[start_idx:end_idx]
    tot_count = len(user_reviews)

    # 사용자의 리뷰 목록 페이지를 렌더링함.
    return render_template(
        "myReview.html",
        datas=data,
        limit=per_page,
        page=page,
        page_count=int((tot_count / per_page) + 1),
        total=tot_count,
        user_id=user_id 
    )

# 사용자의 진행 중인 거래 목록 페이지 라우트
@application.route("/myPageIng/<user_id>")
def my_page_ing(user_id):
    # 로그인되어 있지 않으면 로그인 페이지로 리다이렉션함.
    if 'id' not in session:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))

    # 사용자의 진행 중인 거래 목록을 데이터베이스에서 가져옴.
    ing_items = DB.get_ing_items_by_user_id(user_id)

    # 정렬 모드를 가져옴. (기본값은 'all')
    sort_mode = request.args.get("sort", "all")

    # 정렬 모드에 따라 거래 목록을 필터링함.
    if sort_mode == "direct":
        ing_items = [item for item in ing_items if item.get('trans_mode') == "direct"]
    elif sort_mode == "parcel":
        ing_items = [item for item in ing_items if item.get('trans_mode') == "parcel"]
    elif sort_mode == "nondirect-box":
        ing_items = [item for item in ing_items if item.get('trans_mode') == "nondirect-box"]

    # 페이지 및 페이지당 거래 수를 설정함.
    page = request.args.get("page", 0, type=int)
    per_page = 3

    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    # 현재 페이지에 표시할 거래 데이터를 설정함.
    data = ing_items[start_idx:end_idx]
    tot_count = len(ing_items)

    # 사용자의 진행 중인 거래 목록 페이지를 렌더링함.
    return render_template(
        "myPageIng.html",
        ing_items=data,
        page=page,
        page_count=int((tot_count / per_page) + 1),
        user_id=user_id,
        sort_mode=sort_mode 
    )

# 사용자의 완료된 거래 목록 페이지 라우트
@application.route("/myPageDone/<user_id>")
def my_page_done(user_id):
    # 로그인되어 있지 않으면 로그인 페이지로 리다이렉션함.
    if 'id' not in session:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))

    # 사용자의 완료된 거래 목록을 데이터베이스에서 가져옴.
    done_items = DB.get_done_items_by_user_id(user_id)
    print("Done Items:", done_items)

    # 정렬 모드를 가져옴. (기본값은 'all')
    sort_mode = request.args.get("sort", "all")

    # 정렬 모드에 따라 거래 목록을 필터링함.
    if sort_mode == "direct":
        done_items = [item for item in done_items if item.get('trans_mode') == "direct"]
    elif sort_mode == "parcel":
        done_items = [item for item in done_items if item.get('trans_mode') == "parcel"]
    elif sort_mode == "nondirect-box":
        done_items = [item for item in done_items if item.get('trans_mode') == "nondirect-box"]

    # 페이지 및 페이지당 거래 수를 설정함.
    page = request.args.get("page", 0, type=int)
    per_page = 3

    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    # 현재 페이지에 표시할 거래 데이터를 설정함.
    data = done_items[start_idx:end_idx]
    tot_count = len(done_items)

    # 사용자의 완료된 거래 목록 페이지를 렌더링함.
    return render_template(
        "myPageDone.html",
        done_items=data,
        page=page,
        page_count=int((tot_count / per_page) + 1),
        user_id=user_id,
        sort_mode=sort_mode 
    )


# 비대면 상자 정보
@application.route("/myTradeBox/<name>/")
def view_trade_box_detail(name):
    if 'id' not in session:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('login'))
    # db 받아와 전달
    data = DB.get_item_by_name(name)
    return render_template("my_trade_box.html", name=name, data=data)


if __name__ == "__main__":
    application.run(debug=True)
