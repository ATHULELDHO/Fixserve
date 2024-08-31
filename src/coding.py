from flask import *
from src.dbconnectionnew import *
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = "73467834657"


@app.route("/")
def login():
    return render_template("login_index.html")


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
def block_provider():
    qry = 'SELECT * FROM `serviceprovider` JOIN `login` ON `serviceprovider`.lid = `login`.id JOIN `services` ON `serviceprovider`.`service`=`services`.`id` WHERE `login`.type != "pending"'
    res = selectall(qry)
    return render_template("admin/blockprovider.html", val=res)


@app.route("/complaint_reply")
def complaint_reply():
    id = request.args.get('id')
    session['cid'] = id
    return render_template("admin/complaintReply.html")



@app.route("/insert_reply", methods=['post'])
def insert_reply():
    reply = request.form['textfield']
    qry = "UPDATE `complaint` SET `reply`=%s WHERE `id`=%s"
    iud(qry, (reply, session['cid']))
    return '''<script>alert("Success");window.location="/view_complaint"</script>'''


@app.route("/verify_provider")
def verify_provider():
    qry = 'SELECT * FROM `serviceprovider` JOIN `login` ON `serviceprovider`.lid = `login`.id JOIN `services` ON `serviceprovider`.`service`=`services`.`id` WHERE `login`.type = "pending"'
    res = selectall(qry)
    return render_template("admin/verifyprovider.html", val=res)


@app.route("/accept_provider")
def accept_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="service_provider" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/verify_provider"</script>'''


@app.route("/reject_provider")
def reject_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/verify_provider"</script>'''


@app.route("/block_provider2")
def block_provider2():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="blocked" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/block_provider"</script>'''


@app.route("/unblock_provider")
def unblock_provider():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="service_provider" WHERE id=%s'
    iud(qry,id)
    return '''<script>alert("Success");window.location="/block_provider"</script>'''


@app.route("/view_complaint")
def view_complaint():
        qry = 'SELECT * FROM `complaint` JOIN `user` ON `complaint`.`userid`=`user`.`lid` where reply="pending"'
        res = selectall(qry)
        return render_template("admin/viewcomplaint.html", val=res)


@app.route("/rating_provider")
def rating_provider():
    qry = "SELECT `serviceprovider`.`firstname`,`lastname`,`rate and review`.* FROM `rate and review` JOIN `serviceprovider` ON `rate and review`.`providerid`=`serviceprovider`.`lid` WHERE `rate and review`.`userid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("user/ratingprovider.html", val=res)


@app.route("/add_rating", methods=['post'])
def add_rating():
    qry = "SELECT `serviceprovider`.* FROM `serviceprovider` JOIN  `request` ON `serviceprovider`.`lid`=`request`.`providerid` WHERE `request`.`userid`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("user/add_rating_and_review.html", val=res)


@app.route("/insert_rating_review", methods=['post'])
def insert_rating_review():
    pid = request.form['select']
    rating = request.form['textfield']
    review = request.form['textfield2']

    qry = "INSERT INTO `rate and review` VALUES(NULL, %s,%s,%s,%s,CURDATE())"
    iud(qry,(session['lid'], pid,rating,review))

    return '''<script>alert("Success");window.location="rating_provider"</script>'''


@app.route("/view_request")
def view_request():
    return render_template("provider/viewrequest.html")


@app.route("/admin_home")
def admin_home():
    return render_template("admin/adminhome.html")

@app.route("/provider_home")
def provider_home():
    return render_template("provider/providerhome.html")

@app.route("/user_home")
def user_home():
    return render_template("user/userhome.html")

@app.route("/request_provder")
def request_provder():

    qry = "select * from services"
    res = selectall(qry)

    return render_template("user/requestprovider.html", val2=res)


@app.route("/search_request", methods=['post'])
def search_request():
    pin = request.form['textfield']
    service_needed = request.form['select']

    session['sid'] = service_needed

    print(service_needed)

    qry = "SELECT `serviceprovider`.* FROM `serviceprovider` JOIN `services` ON `serviceprovider`.`service`=`services`.`id` WHERE `serviceprovider`.`pincode`=%s AND `services`.`id`=%s"
    res = selectall2(qry, (pin, service_needed))

    print(res)

    qry = "select * from services"
    res2 = selectall(qry)
    return render_template("user/requestprovider.html", val=res, val2=res2)


@app.route("/send_request")
def send_request():
    id = request.args.get('id')
    session['rid'] = id
    return render_template("user/send_request.html")


@app.route("/insert_request", methods=['post'])
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
def manage_service():
    qry = "SELECT * FROM `services`"
    res = selectall(qry)
    return render_template("admin/manage_services.html", val=res)


@app.route("/add_service", methods=['post'])
def add_service():
    return render_template("admin/add_services.html")


@app.route("/insert_service", methods=['post'])
def insert_service():
    service_name = request.form['textfield']
    qry = "INSERT INTO `services` VALUES(NULL, %s)"
    iud(qry, service_name)
    return '''<script>alert("Successfully inserted");window.location="manage_service"</script>'''


@app.route("/delete_service")
def delete_service():
    id = request.args.get('id')
    qry = "DELETE FROM `services` WHERE `id`=%s"
    iud(qry, id)
    return '''<script>alert("Deleted");window.location="manage_service"</script>'''


@app.route("/request_status")
def request_status():
    print(session['lid'])
    qry = "SELECT `serviceprovider`.`firstname`,`lastname`,`phone`,`services`.`service_name`,`request`.`status` FROM `request` JOIN `serviceprovider` ON `request`.`providerid`=`serviceprovider`.`lid` JOIN `services`ON `request`.`serviceid`=`services`.`id` where request.`userid` = %s"
    res = selectall2(qry, session['lid'])
    return render_template("user/requeststatus.html", val=res)




app.run(debug = True)