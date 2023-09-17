from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Regexp, Length, URL
from wtforms import StringField, SubmitField, SelectField, FileField, TextAreaField, PasswordField


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired(),Length(max=8)])
    phone = StringField("Contact Number", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class VendorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    vendor = SelectField('Category', choices=[('Decorator', 'Decorator'), ('Photographer', 'Photographer'),
                                              ('Caterer', 'Caterer'), ('Florist', 'Florist'),
                                              ('DJ/Musician', 'DJ/Musician'), ('Entertainment', 'Entertainment'),
                                              ('Choreographe', 'Choreographe'), ('Venue', 'Venue'),
                                              ('Other','Other')])
    password = StringField("Password", validators=[DataRequired()])
    phone = StringField("Contact Number", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    price = StringField("MinimumPrice", validators=[DataRequired()])
    img_url = StringField("Image", validators=[DataRequired(), URL()])
    description = TextAreaField('Description')
    submit = SubmitField("Sign Me Up!")

class FilterForm(FlaskForm):
    city = SelectField('city', choices=[])
    price = SelectField('price', choices=[('Low to High'),('High to Low')])
    submit = SubmitField("Search")

class GuestForm(FlaskForm):
    name = StringField("Guest Name", validators=[DataRequired()])
    submit = SubmitField("Add")

class ToDoForm(FlaskForm):
    name = StringField("New ToDo", validators=[DataRequired()])
    submit = SubmitField("Add")