from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #sq lite data base
app.config['SECRET_KEY'] = 'your_secret_key' #security key
app.config['UPLOAD_FOLDER'] = 'static/uploads'#folder uploads for profile pic
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disables unnecessary tracking to reduce memory usag

# Initialize extensions
db = SQLAlchemy(app) # database object relation mapper
bcrypt = Bcrypt(app) #password hashing
socketio = SocketIO(app, cors_allowed_origins="*")# websockets for real time chat # you allow any website to connect it to the user

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)#Ensures the static/uploads folder exists to store profile picture

# Online users storage
online_users = {}

# ---------------- DATABASE MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # nullable cannot have null values
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(300), nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #his creates a foreign key relationship between the Message table and the User tabl
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# ---------------- AUTHENTICATION FORMS ----------------
class PhoneLoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=50)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    profile_pic = FileField("Upload Profile Picture", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField("Sign Up")

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            contacts = User.query.filter(User.id != user.id).all()
            return render_template("chat.html", user=user, contacts=contacts)
        session.pop("user_id", None)
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(full_name=form.full_name.data, phone_number=form.phone_number.data, password=password)
        db.session.add(new_user)
        db.session.commit()
        if form.profile_pic.data:
            pic_filename = f"user_{new_user.id}.png"
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_filename)
            form.profile_pic.data.save(pic_path)
            new_user.profile_pic = pic_filename
            db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("phone_login"))
    return render_template("signup.html", form=form)

@app.route("/phone-login", methods=["GET", "POST"])
def phone_login():
    form = PhoneLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.phone_number.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session["user_id"] = user.id
            session["username"] = user.full_name
            return redirect(url_for("home"))
        flash("Invalid credentials!", "danger")
    return render_template("phone_login.html", form=form)

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("phone_login"))
    user = User.query.get(session["user_id"])
    contacts = User.query.filter(User.id != user.id).all()
    return render_template("chat.html", user=user, contacts=contacts)

@app.route("/chat/<int:receiver_id>")
def chat_with_user(receiver_id):
    if "user_id" not in session:
        return redirect(url_for("phone_login"))
    user = User.query.get(session["user_id"])
    receiver = User.query.get(receiver_id)
    messages = Message.query.filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == receiver.id)) |
        ((Message.sender_id == receiver.id) & (Message.receiver_id == user.id))
    ).order_by(Message.timestamp).all()
    return render_template("chat.html", user=user, receiver=receiver, messages=messages)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# ---------------- SOCKET.IO EVENTS ----------------
@socketio.on("send_message")
def handle_message(data):
    sender_id = session.get("user_id")
    receiver_id = data["receiver_id"]
    message_text = data["message"]
    if sender_id and receiver_id and message_text:
        message = Message(sender_id=sender_id, receiver_id=receiver_id, message=message_text)
        db.session.add(message)
        db.session.commit()
        emit("receive_message", {"sender_id": sender_id, "receiver_id": receiver_id, "message": message_text}, broadcast=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
