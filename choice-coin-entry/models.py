from database import db
from vote import hashing
from enum import unique, Enum
from sqlalchemy import func

class Admin(db.Model):
    __tablename__ = "admin"
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
 
    def __init__(self, username, email, password) -> None:
        self.username = username
        self.email = email
        self.password = hashing(password)
 
 
class Project(db.Model):
    __tablename__ = "project"
 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False, unique=True)
    # category = db.Column(db.Text, nullable=False)
    # target = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(1000), nullable=False, unique=True)
    phrase = db.Column(db.String(512), nullable=False, unique=True)
    number_of_votes = db.Column(db.Integer, default=0)
    votes = db.relationship("Vote", backref="voter", lazy="dynamic")
    participants = db.relationship("Participant", backref="project", lazy="dynamic")
 

@unique
class VoterLevel(Enum):
    EMPLOYEE = 1
    CTO = 5
    CEO = 10

class Voter(db.Model):
    __tablename__ = "voter"
 
    id = db.Column(db.Integer, primary_key=True)
    ssn = db.Column(db.String(30), nullable=False)
    license_id = db.Column(db.String(20), nullable=False)
    # level = db.Column(db.Enum(VoterCategory))
    level = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(1000), nullable=False, unique=True)
    phrase = db.Column(db.String(512), unique=True)
    has_voted = db.Column(db.String(10), default="no")
 
    votes = db.relationship("Vote", backref="leggo", lazy="dynamic")


class Vote(db.Model):
    __tablename__ = "vote"
 
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    voter_id = db.Column(db.Integer, db.ForeignKey("voter.id"))
 
 
class Participant(db.Model):
    __tablename__ = "participant"
 
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(100), nullable=False, unique=True)
    private_key = db.Column(db.String(100), nullable=False, unique=True)