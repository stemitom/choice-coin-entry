from enum import unique
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn
from flask import (
    Flask,
    flash,
    url_for,
    redirect,
    render_template,
    request,
    session
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import func
from vote import algod_client, choice_id, countVotes, electionVoting, hashing


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voters.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    hashed_key = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())

    def __init__(self, username, key) -> None:
        self.username = username
        self.hashed_key = hashing(key)


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=True)
    category = db.Column(db.Text, nullable=False)
    target = db.Column(db.Integer, nullable=False)
    votes = db.relationship("Vote", backref="voter", lazy="dynamic")


class Vote(db.Model):
    __tablename__ = "vote"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    address = db.Column(db.String(100), db.ForeignKey('voter.id'))


class Voter(db.Model):
    __tablename__ = "voter"

    id = db.Column(db.Integer, primary_key=True)
    ssn = db.Column(db.String(30), nullable=False)
    license_id = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(1000), nullable=False, unique=True)
    phrase = db.Column(db.String(512), unique=True)
    votes = db.relationship("Vote", backref="leggo", lazy="dynamic")


finished = False
corporate_finished = False
validated = False


@app.route("/")
def start():
	""" Start page """
	return render_template('index.html')


@app.route('/about/')
def about():
	"""about"""
	return render_template('about.html')


@app.route('/corporate', methods = ['POST','GET'])
def corporate():
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
	return render_template('corporate.html', message = message, error = error)

@app.route('/corporate_creation',methods = ['POST','GET'])
def corporate_create():
	if request.method == 'POST':
		Name = request.form.get('Name')
		Key = hashing(str(request.form.get('Secret')))
		Percentage = request.form.get('Stake')
		Main = hashing(str(request.form.get('Main')))
		if Main == "":
			cur.execute("INSERT INTO corporate (name, Secret, Stake) VALUES(%s,%s,%s)",((Name,Key,Percentage)))
			conn.commit()
	return render_template('corporatecreate.html')


@app.route('/corporatestart', methods = ['POST', 'GET'])
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


@app.route('/corporateend', methods = ['POST', 'GET'])
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