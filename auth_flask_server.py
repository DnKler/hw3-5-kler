from flask import Flask, flash, render_template, request, make_response, redirect, abort, send_from_directory
import random
from pymongo import MongoClient 
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['SECRET_KEY']= 'the secret string'

client = MongoClient('localhost',27017)
db = client.wad

logged_users = {}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

@app.route('/cabinet', methods=["GET", "POST"])
def cabinet():
    if request.cookies:
        sessionid = request.cookies["sessionid"] 
        if sessionid not in logged_users:
            abort(403)
        username = logged_users[sessionid]
        
        if request.method == "POST":
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Successfully saved', 'success')
                imgname = "upload/"+filename
                db.users.update({"name":username}, {"$set": {"img": imgname}})
                return redirect(request.url)
        return render_template("cabinet.html", name=username, picture=db.users.find_one({"name":username})['img'])
    else:
        abort(403)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["name"]
        psw = request.form["password"]
        if request.cookies:
            if request.cookies["sessionid"] in logged_users:
               return "You have already logged in"
        if ( not db.users.find_one({"name":username})) or (not db.users.find_one({"name":username, "password":psw})) : 
            return render_template("login.html")
            
        sessionid = str(random.randint(10**10, 10**20))
        logged_users[sessionid] = username
        resp = make_response(redirect("/cabinet"))
        resp.set_cookie('sessionid', sessionid)
        return resp


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["name"]
        psw1 = request.form["password"]
        psw2 = request.form["password2"]
        if db.users.find_one({"name":username}) : 
            return "This name is already taken"
        if psw1 != psw2:
            return "Passwords are not equal!"
        db.users.insert({"name":username, "password":psw1, "img":"static/lion with computer.jpg"})
        return render_template("login.html")


@app.route('/static/<path:filename>')
def send_from_static(filename):
    return app.send_static_file(filename)
    
@app.route('/upload/<path:filename>')
def send_from_upload(filename):
    return send_from_directory("upload", filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "icons8-lion-100.png", mimetype="image/vnd.microsoft.icon")
    
    
@app.route('/logout', methods=["GET"])
def logout():
    if request.cookies:
        sessionid = request.cookies["sessionid"] 
        if sessionid not in logged_users:
            abort(404)
        name = logged_users[sessionid]
        del logged_users[sessionid]
        return render_template("logout.html", name=name)
    else:
        abort(404)
    
    
#@app.route('/debug')
#def debug():
#    return logged_users


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)