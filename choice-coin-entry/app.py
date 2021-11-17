import os
from flask import Flask, flash, url_for, redirect, render_template, request, session
from vote import hashing
from database import db
from functools import wraps
from decouple import config
from utils import createAccount, sendChoice
from upload_util import allowed_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, current_user

SECRET_KEY = config("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = config("SQLALCHEMY_DATABASE_URI")
UPLOAD_FOLDER = config("UPLOAD_FOLDER")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'voterLogin'
login_manager.init_app(app)

from models import Admin, Project, Voter

@login_manager.user_loader
def load_user(ssn):
    return Voter.query.get(ssn)

def is_admin(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        admin_email = session.get("admin", "")
        admin = Admin.query.filter_by(email=admin_email).first()
        if admin:
            return function(*args, **kwargs)
        flash("You need to be logged in as admin for this action", "danger")
        return redirect(url_for("adminLogIn"))
    return wrap


finished = False
corporate_finished = False
validated = False


@app.route("/test", methods=["GET"])
def test():
    projects = Project.query.all()
    return render_template("test.html", projects=projects)


@app.before_first_request
def create_db():
    db.create_all()


@app.route("/", methods=["GET"])
def home():
    """Start page"""
    return render_template("index.html")


@app.route("/corporate/admin/signup", methods=["GET", "POST"])
def adminSignUp():
    if request.method == "POST":
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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(
            username=username, password=hashing(password)
        ).first()
        if not admin or admin.password != hashing(password):
            flash("Account does not exist", "danger")
            return redirect(url_for("adminLogIn"))
        session["admin"] = admin.email
        flash("Logged in successfully", "success")
        return redirect(url_for("adminLogIn"))
    return render_template("adminLogIn.html")


@app.route("/corporate/admin/signout", methods=["POST"])
@is_admin
def adminLogOut():
    session.pop("admin")
    flash("Logged out successfully", "info")
    return redirect(url_for("adminLogIn"))


@app.route("/corporate/project/add", methods=["GET", "POST"])
@is_admin
def createProject():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("message")
        if "project-image" not in request.files:
            flash("No image file supplied")
            return redirect(request.url)
        image_file = request.files["project-image"]
        if image_file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        try:
            addr, phrase, _ = createAccount()
            print("Account creation successful")
            project = Project(
                title=title,
                image=filename,
                description=description,
                address=addr,
                phrase=phrase,
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
    if request.method == "POST":
        ssn = request.form.get("ssn")
        license_id = request.form.get("license_id")
        category = request.form.get("position")
        if not category in ["CEO", "CTO", "Employee"]:
            flash("Position selected is not valid")
            return render_template("createExecutives.html")
        print(category)
        if Voter.query.filter_by(ssn=ssn).first():
            flash("Voter is already registered", "danger")
            return render_template("createExecutives.html")
        print("Voter section successful")
        voter = Voter(ssn=ssn, license_id=license_id, category=category)
        db.session.add(voter)
        db.session.commit()
        flash("Executive voter created successfully", "success")
        return redirect(url_for("createExecutives"))
    return render_template("createExecutives.html")

@app.route("/corporate/voter/login", methods=["GET", "POST"])
def voterLogIn():
    if request.method == 'POST':
        ssn = request.form.get("ssn")
        voter = Voter.query.filter_by(ssn=ssn).first()
        if voter:
            login_user(voter, remember=False)
            return redirect(url_for('poll'))
        flash("Please check your login details and try again", "danger")
        return redirect(request.url)
    return render_template("voterLogIn.html")


@app.route("/corporate/poll", methods=["GET", "POST"])
@login_required
def poll():
    if request.method == "POST":
        title = (list(request.form.lists())[0][0])
        levelMap = {"CEO": 10, "CTO": 5, "Staff": 2}
        voter = Voter.query.filter_by(ssn=current_user.ssn).first()
        if voter.has_voted:
            flash("You can't vote multiple times", "danger")
            return redirect(request.url)
        project = Project.query.filter_by(title=title).first()
        voteStatus = sendChoice(project.address, stake=levelMap[current_user.category])
        transaction_id = voteStatus[1]
        project.number_of_votes += 1
        voter.has_voted = 1
        db.session.commit()
        flash(f"You have successfully voted. Check your vote transactions at https://testnet.algoexplorer.io/tx/{transaction_id}", "success")
        return redirect(request.url)
    projects = Project.query.all()
    return render_template("poll.html", projects=projects)


@app.route("/about/", methods=["GET"])
def about():
    """about"""
    return render_template("about.html")

@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")


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
    app.run(host="127.0.0.1", debug=True)
