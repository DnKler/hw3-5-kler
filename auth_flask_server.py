from flask import Flask, render_template, request, make_response, redirect, abort
import random
from pymongo import MongoClient 

app = Flask(__name__)
client = MongoClient('localhost',27017)
db = client.wad

logged_users = {}

@app.route('/cabinet')
def cabinet():
    if request.cookies:
        sessionid = request.cookies["sessionid"] 
        if sessionid not in logged_users:
            abort(403)
        return render_template("cabinet.html", name=logged_users[sessionid])
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
        if not db.users.find_one({"name":username}) : 
            return render_template("login.html")
        if not db.users.find_one({"name":username, "password":psw}):
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
        db.users.insert({"name":username, "password":psw1})
        return render_template("login.html")


@app.route('/static/<path:filename>')
def send_from_static(filename):
    return app.send_static_file(filename)
    
    
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