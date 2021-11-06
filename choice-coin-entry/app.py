from flask import Flask, flash, url_for, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from vote import hashing
from database import db
from functools import wraps
from utils import choiceCoinOptIn, createNewAccount, generateAlgorandKeypair, choiceVote

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voters.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = "soft-life"
db.init_app(app)

from models import Admin, Project, Voter

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

@app.before_first_request
def create_db():
	db.create_all()


@app.route("/", methods=["GET"])
def home():
	""" Start page """
	return render_template('index.html')

@app.route("/corporate/admin/signup", methods=["GET", "POST"])
def adminSignUp():
	if request.method == 'POST':
		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password")
		admin = Admin.query.filter_by(email=email).first()
		if admin:
			flash("Admin user already exists", "danger")
			return redirect(url_for("adminSignUp"))
		admin = Admin(username=username, email=email, password=password)
		db.session.add(admin)
		db.session.commit()
		flash("Admin account successfully created. You can login", "success")
		return redirect(url_for("adminLogIn"))
	return render_template("adminSignUp.html")

@app.route("/corporate/admin/login", methods=["GET", "POST"])
def adminLogIn():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")
		admin = Admin.query.filter_by(username=username, password=hashing(password)).first()
		if not admin or admin.password != hashing(password):
			flash("Account does not exist", "danger")
			return redirect(url_for("adminLogIn"))
		session["admin"] = admin.email
		flash("Logged in successfully", "success")
		return redirect(url_for("adminLogIn"))
	return render_template("adminLogIn.html")


@app.route("/corporate/admin/signout", methods=["POST"])
def adminLogOut():
	session.pop("admin")
	flash("Logged out successfully", "info")
	return redirect(url_for("adminLogIn"))

@is_admin

@app.route("/corporate/project/add", methods=["GET", "POST"])
def createProject():
	if request.method == 'POST':
		title = request.form.get("title")
		try:
			address, phrase, privateKey = generateAlgorandKeypair()
			choiceCoinOptIn(address, privateKey)
			project = Project(
				title=title,
				address=address,
				phrase=phrase
			)
			db.session.add(project)
			db.session.commit()
			flash("Project Created", "success")
			return redirect(url_for("createProject"))
		except Exception as e:
			flash(e, "danger")
			return redirect(url_for("createProject"))
	return render_template("createProject.html")

@app.route("/corporate/executives/add", methods=["GET", "POST"])
@is_admin
def createExecutives():
	if request.method == 'POST':
		ssn = request.form.get("ssn")
		license_id = request.form.get("license_id")
		category = request.form.get("category")
		if Voter.query.filter_by(ssn=ssn).first():
			flash("Unable to login, please try again!", "error")
			return render_template("createExecutives.html")
		accountResponse = createNewAccount()
		address = accountResponse["address"]
		phrase = accountResponse["phrase"]
		voter = Voter(
			ssn = ssn,
			license_id=license_id,
			category=category,
			address=address,
			phrase=phrase
		)
		db.session.add(voter)
		db.session.commit()
		flash("Executive voter created successfully", "success")
		flash(address, "warning")
		flash(phrase, "info")
		return redirect(url_for("createExecutives"))
	return render_template("createExecutives.html")

@app.route("/corporate/vote", methods=["GET", "POST"])
def vote():
	levelMap = {
		'CEO': 10,
		'CTO': 5,
		'Staff': 2
	}
	if request.method == 'POST':
		ssn = request.form.get("ssn")
		projectTitle = request.form.get("project")
		voter = Voter.query.filter_by(ssn=ssn)
		project = Project.query.filter_by(title=projectTitle)
		if not voter: 
			flash("You are ineligible to vote", "danger")
			return redirect(url_for("vote"))
		if voter.has_voted == "yes":
			flash("You can't vote multiple times", "danger")
			return redirect(url_for("vote"))
		voteDetails = choiceVote(voter.address, voter.phrase, 
							project.address, levelMap[voter.level] * 1, "Tabulated using Choice Coin")
		transactionID = voteDetails[1]
		if not voteDetails[0]:
			flash("Something occured! Please do try again", "danger")
			return redirect(url_for('vote'))
		message = f"Voted counted. You can can confirm by visiting https://testnet.algoexplorer.io/tx/{transactionID}"
		project.number_of_votes += 1
		db.session.commit()
		flash(message, "success")
		return redirect(url_for('vote'))

@app.route('/about/', methods=["GET"])
def about():
	"""about"""
	return render_template('about.html')

# @app.route('/corporate-start', methods = ['POST', 'GET'])
# def start_corporate():
# 	error = ''
# 	message = ''
# 	global corporate_finished
# 	if request.method == 'POST':
# 		key = hashing(str(request.form.get('Key')))
# 		if key == admin_key:
# 			message = reset_corporate_votes()
# 			corporate_finished = False
# 		else:
# 			error = "Incorrect admin key"
# 	return render_template("start.html", message = message, error = error)


# @app.route('/corporate-end', methods = ['POST', 'GET'])
# def corporate_end():
# 	error = ''
# 	message = ''
# 	global corporate_finished
# 	if request.method == 'POST':
# 		key = hashing(str(request.form.get('Key')))
# 		if key == admin_key:
# 			message = count_corporate_votes()
# 			corporate_finished = True
# 		else:
# 			error = "Incorrect admin key"
# 	return render_template('corporate_end.html', message = message, error = error)


if __name__ == "__main__":
	app.run(host='127.0.0.1', debug=True)