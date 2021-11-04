from . import db
from .vote import hashing
from enum import unique, Enum
from sqlalchemy import func

class Admin(db.Model):
    __tablename__ = "admin"
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
 
    def __init__(self, username, pw) -> None:
        self.username = username
        self.password = hashing(pw)
 
 
class Project(db.Model):
    __tablename__ = "project"
 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=True)
    # category = db.Column(db.Text, nullable=False)
    # target = db.Column(db.Integer, nullable=False)
    votes = db.relationship("Vote", backref="voter", lazy="dynamic")
    participants = db.relationship("Participant", backref="project", lazy="dynamic")
 
 
class Participant(db.Model):
    __tablename__ = "participant"
 
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(100), nullable=False, unique=True)
    private_key = db.Column(db.String(100), nullable=False, unique=True)
 
 
@unique
class VoterCategory(Enum):
    EMPLOYEE = 1
    CTO = 5
    CEO = 10

class Voter(db.Model):
    __tablename__ = "voter"
 
    id = db.Column(db.Integer, primary_key=True)
    ssn = db.Column(db.String(30), nullable=False)
    license_id = db.Column(db.String(20), nullable=False)
    category = db.Column(db.Enum(VoterCategory))
    address = db.Column(db.String(1000), nullable=False, unique=True)
    phrase = db.Column(db.String(512), unique=True)
 
    votes = db.relationship("Vote", backref="leggo", lazy="dynamic")


class Vote(db.Model):
    __tablename__ = "vote"
 
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    voter_id = db.Column(db.Integer, db.ForeignKey("voter.id"))
 
