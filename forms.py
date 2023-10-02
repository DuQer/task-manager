from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class UpdateUserForm(FlaskForm):
    new_username = StringField('New Username', validators=[DataRequired(), Length(min=4, max=20)])


class CreateTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    due_date = DateField('Due Date', validators=[Optional()])
    priority = IntegerField('Priority', validators=[Optional()])


class UpdateTaskForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    due_date = DateField('Due Date', validators=[Optional()])
    priority = IntegerField('Priority', validators=[Optional()])