from flask import Flask, render_template, request, redirect, url_for,flash
from flask_bootstrap import Bootstrap
from forms import RegisterForm, LoginForm, VendorForm, FilterForm, GuestForm, ToDoForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import smtplib



app = Flask(__name__)
Bootstrap(app)
app.secret_key = "any-string-you-want-just-keep-it-secret"

my_email = "#"
password = "#"

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    guests = relationship("Guest")

class Guest(UserMixin, db.Model):
    __tablename__="guests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, ForeignKey('users.id'))

class ToDo(UserMixin, db.Model):
    __tablename__="todo"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, ForeignKey('users.id'))

class Review(UserMixin, db.Model):
    __tablename__="reviews"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    review = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, ForeignKey('users.id'))

class Vendor(UserMixin, db.Model):
    __tablename__ = "vendor"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    vendor = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    price = db.Column(db.String(100))
    img_url = db.Column(db.String(250))
    description = db.Column(db.String(500))


# Create all the tables in the database
db.create_all()

@app.route('/')
def home():
    if current_user!="":
        all_reviews = Review.query.all()
        return render_template("index.html", all_reviews=all_reviews)
    return render_template("index.html")

@app.route("/review",methods=["POST"])
def review():
    if request.method == "POST":
        new_review = Review(

            name=current_user.name,
            review = request.form.get("review"),
            rating = int(request.form.get("ratings")),
            parent_id = current_user.id
        )
        db.session.add(new_review)
        db.session.commit()
    all_reviews = Review.query.all()
    return render_template("index.html",all_reviews=all_reviews , current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/todo",methods=["GET", "POST"])
def todo():
    form = ToDoForm()
    new_todo = ToDo(
        name=form.name.data,
        parent_id=current_user.id
    )
    if (form.name.data != None and form.name.data != ""):
        db.session.add(new_todo)
        db.session.commit()
        form.name.data = ""
        return redirect(url_for('todo'))
    all_todos = ToDo.query.filter_by(parent_id=current_user.id).all()
    return render_template("todo.html", form=form, all_todos=all_todos, current_user=current_user)

@app.route("/todo_delete/<int:user_id>")
def todo_delete(user_id):
    todo_to_delete = ToDo.query.get(user_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route("/guest", methods=["GET", "POST"])
def guest():
    form = GuestForm()
    new_guest = Guest(
        name=form.name.data,
        parent_id=current_user.id
    )
    if(form.name.data!=None and form.name.data!=""):
        db.session.add(new_guest)
        db.session.commit()
        form.name.data =""
        return redirect(url_for('guest'))
    all_guests = Guest.query.filter_by(parent_id=current_user.id).all()
    print(current_user.id)

    return render_template("guestlist.html", form=form,all_guests=all_guests, current_user=current_user)

@app.route("/guest_delete/<int:user_id>")
def guest_delete(user_id):
    guest_to_delete = Guest.query.get(user_id)
    db.session.delete(guest_to_delete)
    db.session.commit()
    return redirect(url_for('guest'))

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('about'))
    return render_template("login.html", form=form, current_user=current_user)



@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash messsage
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            phone=form.phone.data,
            city=form.city.data,
            state=form.state.data
        )
        db.session.add(new_user)
        db.session.commit()

        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for('about'))


    #return render_template("register.html", form=form, current_user=current_user)

@app.route('/vendorregister', methods=["GET", "POST"])
def vendorregister():
    form = VendorForm()
    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash messsage
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_vendor = Vendor(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            vendor = form.vendor.data,
            phone=form.phone.data,
            city=form.city.data,
            state=form.state.data,
            price=form.price.data,
            img_url = form.img_url.data,
            description = form.description.data
        )
        db.session.add(new_vendor)
        db.session.commit()

        # This line will authenticate the user with Flask-Login
        login_user(new_vendor)
        return redirect(url_for('about'))
       # return redirect(url_for("get_all_posts"))

    return render_template("vendorregister.html", form=form, current_user=current_user)

@app.route('/<string:Vendors>',methods=["GET", "POST"])
def decorators(Vendors):
    form = FilterForm()
    city_list = db.session.query(Vendor.city.distinct()).all()
    city_list = [city[0] for city in city_list]
    city_list.insert(0,"All");
    form.city.choices = city_list
    if form.city.data is None or form.city.data=="All":
        if form.price.data=="High to Low":
            vendors = Vendor.query.filter_by(vendor=Vendors).order_by(Vendor.price.desc()).all()
        else:
            vendors = Vendor.query.filter_by(vendor=Vendors).order_by(Vendor.price).all()
    else:
        if form.price.data=="High to Low":
            vendors = Vendor.query.filter_by(vendor=Vendors,city=form.city.data).order_by(Vendor.price.desc()).all()
        else:
            vendors = Vendor.query.filter_by(vendor=Vendors, city=form.city.data).order_by(Vendor.price).all()

    return render_template("vendordisplay.html", vendors=vendors,name=Vendors, form=form, current_user=current_user)


@app.route('/Description/<int:vendor_id>',methods=["GET", "POST"])
def description(vendor_id):

    vendor = Vendor.query.filter_by(id=vendor_id)
    return render_template("description.html", vendor=vendor[0])

@app.route("/email", methods=["POST"])
def email():
    if request.method == "POST":
        message = request.form.get("message")
        subject = request.form.get("subject")
        email = request.form.get("email")
        user_email = current_user.email
        user_name = current_user.name
        user_phone = current_user.phone

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs=my_email,
            msg=f"Subject:{user_name} wants to send you a message via EventO: {subject}\n\n "
                f"This User wants to contact you via EventCo:"
                f"\nName: {user_name},"
                f"\nEmail:{user_email},"
                f"\nPhone No.:{user_phone},"
                f"\nMessage: {message}"
        )
    return redirect(request.referrer)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('about'))

if __name__=="__main__":
    app.run(debug=True)