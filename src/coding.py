from flask import *
from src.dbconnectionnew import *


app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login_code", methods=['post'])
def login_code():
    username = request.form['textfield']
    password = request.form['textfield2']

    qry = "SELECT * FROM `login` WHERE `username`=%s AND `password`=%s"
    val = (username, password)
    res = selectone(qry, val)

    if res is None:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''
    elif res['type'] == "admin":
        return '''<script>alert("Welcome admin");window.location="/admin_home"</script>'''
    elif res['type'] == "service_provider":
        return '''<script>alert("Welcome Service provider");window.location="/provider_home"</script>'''
    elif res['type'] == "user":
        return '''<script>alert("Welcome User");window.location="/user_home"</script>'''
    else:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''


@app.route("/user_registration")
def user_registration():
    return render_template("useReg.html")


@app.route("/provider_registration")
def provider_registration():
    return render_template("providerReg.html")


@app.route("/block_provider")
def block_provider():
    return render_template("admin/blockprovider.html")


@app.route("/complaint_reply")
def complaint_reply():
    return render_template("complaintReply.html")


@app.route("/verify_provider")
def verify_provider():
    return render_template("admin/verifyprovider.html")


@app.route("/view_complaint")
def view_complaint():
    return render_template("admin/viewcomplaint.html")

@app.route("/rating_provider")
def rating_provider():
    return render_template("ratingprovider.html")


@app.route("/view_request")
def view_request():
    return render_template("viewrequest.html")


@app.route("/admin_home")
def admin_home():
    return render_template("admin/adminhome.html")

@app.route("/provider_home")
def provider_home():
    return render_template("providerhome.html")

@app.route("/user_home")
def user_home():
    return render_template("userhome.html")

@app.route("/request_provder")
def request_provder():
    return render_template("requestprovider.html")

@app.route("/request_status")
def request_status():
    return render_template("requeststatus.html")




app.run(debug = True)