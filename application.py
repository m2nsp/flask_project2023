from flask import Flask, render_template, request

application = Flask(__name__)

@application.route("/", methods=['GET', 'POST'])
def hello():
    return render_template("index.html")

@application.route("/list_post", methods=['GET', 'POST'])
def view_list():
    return render_template("list.html")

@application.route("/review_post", methods=['GET', 'POST'])
def view_review():
    return render_template("review.html")

@application.route("/reg_items_post", methods=['GET', 'POST'])
def reg_item():
    return render_template("reg_items.html")

@application.route("/reg_reviews_post", methods=['GET', 'POST'])
def reg_review():
    return render_template("reg_reviews.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0')
