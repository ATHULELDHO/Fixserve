from flask import *
from src.dbconnectionnew import *
import os
from werkzeug.utils import secure_filename
import razorpay
import functools


from flask_mail import *


app = Flask(__name__)

app.secret_key = "73467834657"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use the server for your mail service
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'fixserve37@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'pzky pjcq qtes itgj'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = ('Food For Life-Donation And Distribution Management System', 'foodforlifedonation@gmail.com')

mail = Mail(app)


@app.route("/")
def login():
    return render_template("login_index.html")


def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('login_index.html')
        return func()

    return secure_function


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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
        session['lid'] = res['id']
        return '''<script>alert("Welcome admin");window.location="/admin_home"</script>'''
    elif res['type'] == "service_provider":
        session['lid'] = res['id']
        return '''<script>alert("Welcome Service provider");window.location="/provider_home"</script>'''
    elif res['type'] == "user":
        session['lid'] = res['id']
        return '''<script>alert("Welcome User");window.location="/user_home"</script>'''
    elif res['type'] == "rejected":
        session['lid'] = res['id']
        return '''<script>alert("Your request have been rejected by admin");window.location="/"</script>'''
    elif res['type'] == "pending":
        session['lid'] = res['id']
        return '''<script>alert("Your Registration is under processing");window.location="/"</script>'''
    else:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''


@app.route("/user_registration")
def user_registration():
    return render_template("useReg.html")


@app.route("/userregister_code", methods=['post'])
def userregister_code():
    fname = request.form["textfield"]
    lname = request.form["textfield2"]
    email = request.form["textfield3"]
    phno = request.form["textfield4"]
    address = request.form["textfield5"]
    username = request.form["textfield6"]
    password = request.form["textfield7"]

    qry = "INSERT INTO `login` VALUES(NULL, %s, %s, 'user')"
    val = (username, password)
    id = iud(qry, val)

    qry = "INSERT INTO `user` VALUES(NULL, %s, %s, %s, %s, %s, %s)"
    val = (id, fname, lname, email, phno, address)

    iud(qry, val)

    return '''<script>alert("Successfully registered");window.location="/"</script>'''


@app.route("/provider_registration")
def provider_registration():
    qry = "SELECT * FROM `services`"
    res = selectall(qry)
    return render_template("providerReg.html", val=res)


@app.route("/proregister_code", methods=['post'])
def proregister_code():
    fname = request.form["textfield"]
    lname = request.form["textfield2"]
    email = request.form["textfield3"]
    phno = request.form["textfield4"]
    place = request.form["textfield5"]
    pin = request.form["textfield6"]
    service = request.form["textfield7"]
    doc = request.files["file2"]
    noc = request.files["file"]
    username = request.form["textfield8"]
    password = request.form["textfield9"]

    doc_name = secure_filename(doc.filename)
    doc.save(os.path.join("static/uploads", doc_name))

    noc_name = secure_filename(noc.filename)
    noc.save(os.path.join("static/uploads", noc_name))


    qry = "INSERT INTO `login` VALUES(NULL, %s, %s, 'pending')"
    val = (username, password)
    id = iud(qry, val)

    qry = "INSERT INTO `serviceprovider` VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (id, fname, lname, email, phno, place, pin, service, doc_name, noc_name)

    iud(qry, val)

    return '''<script>alert("Successfully registered");window.location="/"</script>'''




@app.route("/block_provider")
@login_required

def block_provider():
    qry = 'SELECT * FROM `serviceprovider` JOIN `login` ON `serviceprovider`.lid = `login`.id JOIN `services` ON `serviceprovider`.`service`=`services`.`id` WHERE `login`.type != "pending"'
    res = selectall(qry)
    return render_template("admin/blockprovider.html", val=res)


@app.route("/complaint_reply")
@login_required
def complaint_reply():
    id = request.args.get('id')
    session['cid'] = id
    return render_template("admin/complaintReply.html")



@app.route("/insert_reply", methods=['post'])
@login_required
def insert_reply():
    reply = request.form['textfield']
    qry = "UPDATE `complaint` SET `reply`=%s WHERE `id`=%s"
    iud(qry, (reply, session['cid']))
    return '''<script>alert("Success");window.location="/view_complaint"</script>'''


@app.route("/verify_provider")
@login_required
def verify_provider():
    qry = 'SELECT * FROM `serviceprovider` JOIN `login` ON `serviceprovider`.lid = `login`.id JOIN `services` ON `serviceprovider`.`service`=`services`.`id` WHERE `login`.type = "pending"'
    res = selectall(qry)
    return render_template("admin/verifyprovider.html", val=res)


@app.route("/accept_provider")
@login_required
def accept_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="service_provider" WHERE id=%s'
    iud(qry,id)


    qry = "SELECT * FROM `serviceprovider` WHERE lid=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('fixserve37@gmail.com', 'pzky pjcq qtes itgj')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been successfully accepted by admin")
        print(msg)
        msg['Subject'] = 'hey there'
        msg['To'] = email
        msg['From'] = 'fixserve37@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])


    return '''<script>alert("Success");window.location="/verify_provider"</script>'''


@app.route("/reject_provider")
@login_required
def reject_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE id=%s'
    iud(qry,id)

    qry = "SELECT * FROM `serviceprovider` WHERE lid=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('fixserve37@gmail.com', 'pzky pjcq qtes itgj')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been rejected by admin")
        print(msg)
        msg['Subject'] = 'hey there'
        msg['To'] = email
        msg['From'] = 'fixserve37@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])

    return '''<script>alert("Success");window.location="/verify_provider"</script>'''


@app.route("/block_provider2")
@login_required
def block_provider2():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="blocked" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/block_provider"</script>'''


@app.route("/unblock_provider")
@login_required
def unblock_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="service_provider" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/block_provider"</script>'''


@app.route("/view_complaint")
@login_required
def view_complaint():
        qry = 'SELECT * FROM `complaint` JOIN `user` ON `complaint`.`userid`=`user`.`lid` where reply="pending"'
        res = selectall(qry)
        return render_template("admin/viewcomplaint.html", val=res)


@app.route("/rating_provider")
@login_required
def rating_provider():
    qry = "SELECT `serviceprovider`.`firstname`,`lastname`,`rate and review`.* FROM `rate and review` JOIN `serviceprovider` ON `rate and review`.`providerid`=`serviceprovider`.`lid` WHERE `rate and review`.`userid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("user/ratingprovider.html", val=res)


@app.route("/add_rating", methods=['post'])
@login_required
def add_rating():
    qry = "SELECT `serviceprovider`.* FROM `serviceprovider` JOIN  `request` ON `serviceprovider`.`lid`=`request`.`providerid` WHERE `request`.`userid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("user/add_rating_and_review.html", val=res)


@app.route("/insert_rating_review", methods=['post'])
@login_required
def insert_rating_review():
    pid = request.form['select']
    rating = request.form['textfield']
    review = request.form['textfield2']

    qry = "INSERT INTO `rate and review` VALUES(NULL, %s,%s,%s,%s,CURDATE())"
    iud(qry,(session['lid'], pid,rating,review))

    return '''<script>alert("Success");window.location="rating_provider"</script>'''


@app.route("/view_request")
@login_required
def view_request():
    qry = "SELECT `user`.`firstname`, `lastname`, `request`.*,`services`.service_name FROM `request` JOIN `user` ON `request`.`userid`=`user`.`lid` JOIN `services` ON `request`.`serviceid`=`services`.id WHERE `request`.`providerid`=%s and request.status='pending'"
    res = selectall2(qry, session['lid'])
    return render_template("provider/viewrequest.html", val = res)


@app.route("/manage_request")
@login_required
def manage_request():
    qry = "SELECT `user`.`firstname`, `lastname`, `request`.*,`services`.service_name FROM `request` JOIN `user` ON `request`.`userid`=`user`.`lid` JOIN `services` ON `request`.`serviceid`=`services`.id WHERE `request`.`providerid`=%s and request.status='accepted'"
    res = selectall2(qry, session['lid'])
    return render_template("provider/manage_request.html", val = res)


@app.route("/update_status")
@login_required
def update_status():
    id = request.args.get('id')
    session['requpid'] = id

    qry = "SELECT * FROM `provider_reply` WHERE rid=%s"
    res = selectone(qry,id)

    return render_template("provider/update status.html", val=res)


@app.route("/insert_status", methods=['post'])
@login_required
def insert_status():
    status = request.form['textfield2']
    qry = "UPDATE `provider_reply` SET `reply`=%s WHERE `rid`=%s"
    iud(qry, (status, session['requpid']))
    return '''<script>alert("Success");window.location="manage_request"</script>'''


@app.route("/mark_as_completed")
@login_required
def mark_as_completed():
    id = request.args.get('id')
    qry = "UPDATE `request` SET `status`='completed' WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Success");window.location="manage_request"</script>'''


@app.route("/accept_request1")
def accept_request1():
    id = request.args.get('id')
    session['rid'] = id
    return render_template("provider/add_reply.html")


@app.route("/accept_request", methods=['post'])
@login_required
def accept_request():
    amount = request.form['textfield']
    reply = request.form['textfield2']
    qry = "UPDATE `request` SET `status`='accepted' WHERE `id`=%s"
    iud(qry, session['rid'])

    qry = "INSERT INTO `provider_reply` VALUES(NULL, %s, %s, %s)"
    iud(qry, (session['rid'], amount, reply))

    return '''<script>alert("Request Accepted");window.location="/view_request"</script>'''


@app.route("/reject_request")
@login_required
def reject_request():
    id = request.args.get('id')
    qry = "UPDATE `request` SET `status`='rejected' WHERE `id`=%s"
    iud(qry,id)
    return '''<script>alert("Request Rejected");window.location="/view_request"</script>'''


@app.route("/admin_home")
@login_required
def admin_home():
    return render_template("admin/admin_index.html")

@app.route("/provider_home")
@login_required
def provider_home():
    return render_template("provider/provider_index.html")


@app.route("/view_rating_provider")
@login_required
def view_rating_provider():
    qry = "SELECT `user`.`firstname`,`user`.`lastname`,`rate and review`.* FROM `rate and review` JOIN `user` ON `rate and review`.`userid`=`user`.`lid` WHERE `rate and review`.`providerid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("provider/view_rating_and_review.html", val=res)


@app.route("/user_home")
@login_required
def user_home():
    return render_template("user/user_index.html")

@app.route("/request_provder")
@login_required
def request_provder():

    qry = "select * from services"
    res = selectall(qry)

    return render_template("user/requestprovider.html", val2=res)


@app.route("/search_request", methods=['post'])
@login_required
def search_request():
    pin = request.form['textfield']
    service_needed = request.form['select']

    session['sid'] = service_needed

    print(service_needed)

    qry = "SELECT `serviceprovider`.* FROM `serviceprovider` JOIN `services` ON `serviceprovider`.`service`=`services`.`id` JOIN `login` ON `serviceprovider`.`lid`=`login`.id WHERE `serviceprovider`.`pincode`=%s AND `services`.`id`=%s AND `login`.`type`='service_provider'"
    res = selectall2(qry, (pin, service_needed))

    print(res)

    qry = "select * from services"
    res2 = selectall(qry)
    return render_template("user/requestprovider.html", val=res, val2=res2)


@app.route("/send_request")
@login_required
def send_request():
    id = request.args.get('id')
    session['rid'] = id
    return render_template("user/send_request.html")


@app.route("/insert_request", methods=['post'])
@login_required
def insert_request():
    details = request.form['textfield']
    photo = request.files['file']
    lati = request.form['textfield3']
    longi = request.form['textfield4']

    photo_name = secure_filename(photo.filename)
    photo.save(os.path.join("static/uploads", photo_name))

    qry = 'INSERT INTO `request` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,curdate(),"pending")'
    iud(qry, (session['lid'], session['rid'], session['sid'], details, photo_name, lati, longi))

    return '''<script>alert("Request send successfully");window.location="request_provder"</script>'''


@app.route("/manage_service")
@login_required
def manage_service():
    qry = "SELECT * FROM `services`"
    res = selectall(qry)
    return render_template("admin/manage_services.html", val=res)


@app.route("/add_service", methods=['post'])
@login_required
def add_service():
    return render_template("admin/add_services.html")


@app.route("/insert_service", methods=['post'])
@login_required
def insert_service():
    service_name = request.form['textfield']
    qry = "INSERT INTO `services` VALUES(NULL, %s)"
    iud(qry, service_name)
    return '''<script>alert("Successfully inserted");window.location="manage_service"</script>'''


@app.route("/delete_service")
@login_required
def delete_service():
    id = request.args.get('id')
    qry = "DELETE FROM `services` WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Deleted");window.location="manage_service"</script>'''


@app.route("/request_status")
@login_required
def request_status():
    print(session['lid'])
    qry = "SELECT `serviceprovider`.`firstname`,`lastname`,`phone`,`services`.`service_name`,`request`.`status`,request.id FROM `request` JOIN `serviceprovider` ON `request`.`providerid`=`serviceprovider`.`lid` JOIN `services`ON `request`.`serviceid`=`services`.`id` where request.`userid` = %s"
    res = selectall2(qry, session['lid'])
    return render_template("user/requeststatus.html", val=res)


@app.route('/pay_now')
@login_required
def pay_now():
    id = request.args.get('id')
    session['pay_req_amt_id'] = id

    qry = "SELECT * FROM `provider_reply` WHERE rid=%s"
    res = selectone(qry,id)

    session['amt'] = int(res['amount']) * 100

    session['actual_amt'] = res['amount']

    qry = "SELECT * FROM `payment` WHERE rid=%s"
    res2 = selectone(qry, id)

    if res2 is not None:
        return '''<script>alert("Already payed");window.location="request_status"</script>'''
    else:
        return render_template("user/payment.html", amt=res['amount'])


@app.route("/view_provider_reply")
@login_required
def view_provider_reply():
    id = request.args.get('id')
    qry = "SELECT * FROM `provider_reply` WHERE rid=%s"
    res = selectall2(qry, id)
    return render_template("user/view_provider_reply.html", val=res)


@app.route("/complaint")
@login_required
def complaint():
    qry = "SELECT * FROM `complaint` WHERE userid=%s"
    res = selectall2(qry, session['lid'])
    return render_template("user/complaint.html", val=res)


@app.route('/new_complaint', methods=['post'])
@login_required
def new_complaint():
    return render_template("user/new_complaint.html")


@app.route("/insert_complaint", methods=['post'])
@login_required
def insert_complaint():
    complaint = request.form['textfield']
    qry = "INSERT INTO `complaint` VALUES(NULL, %s, %s, curdate(), 'pending')"
    iud(qry, (session['lid'], complaint))
    return '''<script>alert("Success");window.location="complaint"</script>'''


@app.route('/user_pay_proceed', methods=['post'])
@login_required
def user_pay_proceed():
    client = razorpay.Client(auth=("rzp_test_edrzdb8Gbx5U5M", "XgwjnFvJQNG6cS7Q13aHKDJj"))
    print(client)
    payment = client.order.create({'amount': session['amt'], 'currency': "INR", 'payment_capture': '1'})
    return render_template('UserPayProceed.html',p=payment)


@app.route('/user_pay_complete', methods=['post'])
@login_required
def user_pay_complete():

    qry = "INSERT INTO `payment` VALUES(NULL, %s, %s, CURDATE())"
    iud(qry, (session['pay_req_amt_id'], session['actual_amt']))

    return '''<script>alert("payment successful");window.location="request_status"</script>'''


@app.route("/payment_details")
@login_required
def payment_details():
    qry = "SELECT `user`.`firstname`,`lastname`,`services`.`service_name`,`payment`.* FROM `user` JOIN `request` ON `user`.lid=`request`.userid JOIN `services` ON `request`.`serviceid`=`services`.id JOIN `payment` ON `request`.id=`payment`.rid WHERE `request`.`providerid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("provider/view_payment.html", val=res)


app.run(debug = True)