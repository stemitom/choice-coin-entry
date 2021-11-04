from enum import unique, IntEnum, Enum
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn
from flask import Flask, flash, url_for, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import func
from vote import algod_client, choice_id, countVotes, electionVoting, hashing
from functools import wraps
from .models import Admin, Project, Voter, Vote

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voters.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def is_admin(function):
	@wraps(function)
	def wrap(*args, **kwargs):
		admin_email = session.get("admin", "")
		admin = Admin.query.filter_by(email=admin_email).first()
		if admin:
			return function(*args, **kwargs)
		flash("You need to be logged in as admin for this action", "danger")
		return redirect(url_for("admin_login"))
	return wrap


finished = False
corporate_finished = False
validated = False


@app.route("/")
def start():
	""" Start page """
	return render_template('index.html')

@app.route("/corporate/admin/signup")
def adminSignUp():
	if request.method == 'POST':
		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password")
		admin = Admin.query.filter_by(email=email).first()
		if admin:
			flash("Admin user already exists", "danger")
			return redirect(url_for("adminSignUp"))
		admin = Admin(username=username, password=password)
		db.session.add(admin)
		db.session.commit()
		flash("Admin account successfully created", "success")
		return redirect(url_for("adminLogIn"))
	return render_template(url_for("adminSignUp.html"))

@app.route("/corporate/admin/login")
def adminLogIn():
	if request.method == 'POST':
		email = request.form.get("username")
		password = request.form.get("password")
		admin = Admin.query.filter_by(email=email).first()
		if not admin or admin.password != password:
			flash("Account does not exist", "danger")
			return redirect(url_for("home"))
		session["admin"] = admin.email
		flash("Logged in successfully", "success")
		return redirect(url_for("home"))
	return render_template("adminLogIn.html")


@app.route("/corporate/admin/signout")
def adminLogOut():
	session.pop("admin")
	flash("Logged out successfully", "info")
	return redirect(url_for("adminLogIn"))

@app.route("/corporate/project/add")
@is_admin
def createProject():
	if request.method == 'POST':
		title = request.form.get("title")
		creatorEmail = session.get("email", "")
		admin = Admin.query.filter_by(email=creatorEmail).first()
		project = Project.query.filter_by(title=title)
		db.session.add(project)
		db.session.commit(project)
		return redirect(url_for("createProject"))
	return render_template("createProject.html")

@app.route("/corporate/executives/add")
@is_admin
def createExecutives():
	if request.method == 'POST':
		ssn = request.form.get("ssn")
		license_id = request.form.get("license_id")
		if Voter.

@app.route('/corporate/vote', methods = ['POST','GET'])
def corporatevote():
	error = ''
	message = ''
	if request.method == 'POST':
		Key = hashing(str(request.form.get('Secret')))
		Percentage = request.form.get('Stake')
		vote = request.values.get("options")
		cur.execute("SELECT * FROM corporate WHERE Secret = %s and Stake = %s",(Key,Percentage))
		check = cur.fetchone()
		if check:
			if vote == 'option1':
				vote = "YES"
				message = corporate_voting(vote,Percentage)
				cur.execute("DELETE FROM corporate WHERE Secret = %s and Stake = %s",(Key,Percentage))
				conn.commit()
			elif vote == 'option2':
				vote = "NO"
				message = corporate_voting(vote,Percentage)
				cur.execute("DELETE FROM corporate WHERE Secret = %s and Stake = %s",(Key,Percentage))
				conn.commit()
			else:
				error = "You did not enter a vote"
		else:
			error = "Your information was incorrect"
	elif corporate_finished == True:
		message = count_corporate_votes()
		return render_template('end.html' ,message = message, error = error)
	return render_template('corporatevote.html', message = message, error = error)

# @app.route('/corporate/voter/create',methods = ['POST','GET'])
# def corporate_create():
# 	if request.method == 'POST':
# 		Name = request.form.get('Name')
# 		Key = hashing(str(request.form.get('Secret')))
# 		Percentage = request.form.get('Stake')
# 		Main = hashing(str(request.form.get('Main')))
# 		if Main == "":
# 			cur.execute("INSERT INTO corporate (name, Secret, Stake) VALUES(%s,%s,%s)",((Name,Key,Percentage)))
# 			conn.commit()
# 	return render_template('corporatecreate.html')

@app.route('/corporate/voter/create',methods = ['POST','GET'])
def corporate_create():
	if request.method == 'POST':
		name = request.form.get('name')
		secret = hashing(request.form.get(''))
		rank = request.values.get()



@app.route('/corporate-start', methods = ['POST', 'GET'])
def start_corporate():
	error = ''
	message = ''
	global corporate_finished
	if request.method == 'POST':
		key = hashing(str(request.form.get('Key')))
		if key == admin_key:
			message = reset_corporate_votes()
			corporate_finished = False
		else:
			error = "Incorrect admin key"
	return render_template("start.html", message = message, error = error)


@app.route('/corporate-end', methods = ['POST', 'GET'])
def corporate_end():
	error = ''
	message = ''
	global corporate_finished
	if request.method == 'POST':
		key = hashing(str(request.form.get('Key')))
		if key == admin_key:
			message = count_corporate_votes()
			corporate_finished = True
		else:
			error = "Incorrect admin key"
	return render_template('corporate_end.html', message = message, error = error)


if __name__ == "__main__":
	app.run(host='127.0.0.1', debug=True)



# @app.route('/start', methods = ['POST', 'GET'])
# def start_voting():
# 	error = ''
# 	message = ''
# 	global finished
# 	if request.method == 'POST':
# 		key = hashing(str(request.form.get('Key')))
# 		if key == '09a1d01b5b120d321de9529369640316ddb120870df1ec03b3f2c6dd39c1ff6ecf8de5e56eb32d79c9d06240eaf5de027f6e7b9df2e2e1a4cb38dd548460b757':
# 			message = reset_votes()
# 			finished = False
# 		else:
# 			error = "Incorrect admin key"
# 	return render_template("start.html", message = message, error = error)


# @app.route('/create', methods = ['POST','GET'])
# def create():
# 	if request.method == 'POST':
# 		Social = hashing(str(request.form.get('Social')))
# 		Drivers = hashing(str(request.form.get('Drivers')))
# 		Key = hashing(str(request.form.get('Key')))
# 		if str(Key) == '09a1d01b5b120d321de9529369640316ddb120870df1ec03b3f2c6dd39c1ff6ecf8de5e56eb32d79c9d06240eaf5de027f6e7b9df2e2e1a4cb38dd548460b757':
# 			cur.execute("INSERT INTO USER (DL, SS) VALUES(?,?)",((Drivers,Social)))
# 			con.commit()
# 	return render_template('create.html')



# @app.route('/end', methods = ['POST','GET'])
# def end():
# 	error = ''
# 	message = ''
# 	global finished
# 	if request.method == 'POST':
# 		key = hashing(str(request.form.get('Key')))
# 		if key == '09a1d01b5b120d321de9529369640316ddb120870df1ec03b3f2c6dd39c1ff6ecf8de5e56eb32d79c9d06240eaf5de027f6e7b9df2e2e1a4cb38dd548460b757':
# 			message = count_votes()
# 			finished = True
# 		else:
# 			error = "Incorrect admin key"
# 	return render_template("end.html", message = message, error = error)


# @app.route('/vote', methods = ['POST','GET'])
# def vote():
# 	error = ''
# 	message = ''
# 	global validated
# 	validated = False
# 	if request.method == 'POST':
# 		Social = hashing(str(request.form.get('Social')))
# 		Drivers = hashing(str(request.form.get('Drivers')))
# 		cur.execute("SELECT * FROM USER WHERE SS = ? AND DL = ?",(Social,Drivers))
# 		account = cur.fetchone()
# 		if account:
# 			cur.execute("DELETE FROM USER WHERE SS = ? and DL = ?",(Social,Drivers))
# 			con.commit()
# 			validated = True
# 			return redirect(url_for('submit'))
# 		else:
# 			error = 'Your info is incorrect'
# 	elif finished == True:
# 		message = count_votes()
# 		return render_template("end.html", message = message, error = error)
# 	return render_template('vote.html', message = message, error = error)


# @app.route('/submit', methods = ['POST', 'GET'])
# def submit():
# 	error = ''
# 	message = ''
# 	global validated
# 	if not validated:
# 		return redirect(url_for('vote'))
# 	else:
# 		if request.method == 'POST':
# 			 vote = request.values.get("options")
# 			 if vote == 'option1':
# 				 vote = "YES"
# 				 message = election_voting(vote)
# 			 elif vote == 'option2':
# 				 vote = "NO"
# 				 message = election_voting(vote)
# 			 else:
# 				 error = "You did not enter a vote"
# 	return render_template('submit.html', message = message, error = error)

@app.route('/about/')
def about():
	"""about"""
	return render_template('about.html')
