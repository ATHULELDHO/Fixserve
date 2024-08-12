from flask import *
from src.dbconnectionnew import *


app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/user_registration")
def user_registration():
    return render_template("useReg.html")


@app.route("/provider_registration")
def provider_registration():
    return render_template("providerReg.html")


@app.route("/block_provider")
def block_provider():
    return render_template("blockprovider.html")


@app.route("/complaint_reply")
def complaint_reply():
    return render_template("complaintReply.html")


@app.route("/verify_provider")
def verify_provider():
    return render_template("verifyprovider.html")


@app.route("/view_complaint")
def view_complaint():
    return render_template("viewcomplaint.html")

@app.route("/rating_provider")
def rating_provider():
    return render_template("ratingprovider.html")


@app.route("/view_request")
def view_request():
    return render_template("viewrequest.html")


@app.route("/admin_home")
def admin_home():
    return render_template("adminhome.html")

@app.route("/provider_home")
def provider_home():
    return render_template("providerhome.html")

@app.route("/user_home")
def user_home():
    return render_template("userhome.html")

app.run(debug = True)