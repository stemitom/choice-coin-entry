from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, SubmitField, IntegerField, SelectMultipleField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length


class AdminForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=0, max=50)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=2)])
    secret_key = PasswordField("Secret Key", validators=[DataRequired()])
    submit = SubmitField("Create Admin Account")


class ProjectForm(FlaskForm):
    name = StringField(
        "Project Name", validators=[DataRequired(), Length(min=2, max=20)]
    )
    category = StringField("Category", validators=[DataRequired()])
    submit = SubmitField("Add Poll")


class VoterForm(FlaskForm):
    ssn = StringField(
        "Social Security Number", validators=[DataRequired(), Length(min=8, max=20)]
    )
    license_id = StringField(
        "License Identification", validators=[DataRequired(), Length(min=5, max=15)]
    )
    category = SelectMultipleField(
        "Level",
        choices=[("newbie", "NEWBIE"), ("master", "MASTER"), ("emeritus", "EMERITUS")],
    )
    admin_key = StringField(
        "Admin Password", PasswordField[DataRequired(), Length(min=2)]
    )
    submit = SubmitField("Create Voter Accounts")


class VoteForm(FlaskForm):
    project = StringField("Project ID", validators=[DataRequired()])
    secret_key = PasswordField("Secret Key", validators=[DataRequired()])
    submit = SubmitField("Submit Ballot")
