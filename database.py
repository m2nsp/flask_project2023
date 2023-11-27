import pyrebase
import json 

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        
    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "email": data['email']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").child(data['id']).set(user_info)
            print(data)
            return True
        else:
            return False
        
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        print("users###", users.val())
        if str(users.val()) == "None": #first registration
            return True
        else:
            for res in users.each():
                value = res.val()

                if value['id'] == id_string:
                    return False
            return True
        
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value = []
        for res in users.each():
            value = res.val()

            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False

    def insert_item(self, name, data, img_path, trade_type, end_date, min_price, max_price, user_id, post_date, transaction):
        item_info ={
            "product_description": data['product_description'],
            "img_path": img_path,
            "trade_type": data['trade_type'],
            "regular_price": data['regular_price'],
            "end_date": data['end_date'],
            "min_price": data['min_price'],
            "max_price": data['max_price'],
            "user_id": user_id,
            "post_date": post_date,
            "transaction": transaction
        }
        self.db.child("item").child(name).set(item_info)
        print(data, img_path)
        return True
    
    def get_items(self ):
        items = self.db.child("item").get().val()
        return items
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        print("###########",name)
        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
        return target_value
    
    def reg_buy(self, data):
        buy_info = {
            "trans_mode" : data['transMode'],   # 결제 정보 (직거래, 경매, 비대면 상자)
            "trans_media" : data['transMedia']  # 결제 수단 (카카오페이, 직거래, 카드, etc)
        }
        self.db.child("trans_info").set(buy_info)
        return True

    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""
        if hearts.val() == None:
            return target_value
        for res in hearts.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()
        return target_value
    
    def update_heart(self, user_id, isHeart, item):
        heart_info = {
            "interested" : isHeart
        }
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True
