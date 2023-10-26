from flask import Flask, render_template, request

application = Flask(__name__)

@application.route("/", methods=['POST'])
def hello():
    return render_template("index.html")

@application.route("/list_post", methods=['POST'])
def view_list():
    return render_template("list.html")

@application.route("/review_post", methods=['POST'])
def view_review():
    return render_template("review.html")

@application.route("/reg_items_post", methods=['POST'])
def reg_item():
    return render_template("reg_items.html")

@application.route("/reg_reviews_post", methods=['POST'])
def reg_review():
    return render_template("reg_reviews.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    data=request.form
    return render_template("submit_item_result.html", data=data)

if __name__ == "__main__":
    application.run(host='0.0.0.0')