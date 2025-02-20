from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, send, emit
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import datetime

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

# Ensure profile picture directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Model for Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(300), nullable=True)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
# Login Form (Only for existing users)
class PhoneLoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Sign Up Form (For new users)
class SignUpForm(FlaskForm):
    full_name = StringField(
        "Full Name", 
        validators=[DataRequired(), Length(min=3, max=50)]
    )

    phone_number = StringField(
        "Phone Number", 
        validators=[DataRequired(), Length(min=10, max=15)]
    )

    password = PasswordField(
        "Password", 
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )

    profile_pic = FileField("Upload Profile Picture", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField("Sign Up")
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# Home Route
@app.route("/")
def home():
    """Redirects logged-in users to chat page."""
    receiver = None 
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        receiver = User.query.filter(User.id != user.id).first()

    if receiver:
            return redirect(url_for("chat_with_user", receiver_id=receiver.id))
    # else:
    #         return render_template("no_chat_available.html")  # Prevent infinite loop

    return render_template("index.html")

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        full_name = form.full_name.data
        phone_number = form.phone_number.data
        password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # Check if user already exists
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            flash("Phone number already registered!", "danger")
            return redirect(url_for("signup"))

        # Create new user
        new_user = User(full_name=full_name, phone_number=phone_number, password=password)
        db.session.add(new_user)
        db.session.commit()  # ✅ Save user first to get ID

        # Handle profile picture upload
        if form.profile_pic.data:
            pic_filename = f"user_{new_user.id}.png"
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_filename)
            form.profile_pic.data.save(pic_path)
            new_user.profile_pic = pic_filename  # Store filename in DB
            db.session.commit()  # ✅ Save filename after updating

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("phone_login"))  # ✅ Redirect to correct login route

    return render_template("signup.html", form=form)

# Login Route
@app.route("/phone-login", methods=["GET", "POST"])
def phone_login():
    form = PhoneLoginForm()

    if form.validate_on_submit():
        phone_number = form.phone_number.data
        password = form.password.data

        # Check if user exists
        user = User.query.filter_by(phone_number=phone_number).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")

            # Find another user to chat with (not the logged-in user)
            receiver = User.query.filter(User.id != user.id).first()
            if receiver:
                return redirect(url_for("chat_with_user", receiver_id=receiver.id))
            else:
                # ✅ Instead of redirecting to "no chat available", create a new chat with a dummy user
                new_user = User(full_name="ChatBot", phone_number="0000000000", password=bcrypt.generate_password_hash("password").decode("utf-8"))
                db.session.add(new_user)
                db.session.commit()

                flash("New chat created!", "success")
                return redirect(url_for("chat_with_user", receiver_id=new_user.id))

        flash("Invalid phone number or password!", "danger")

    return render_template("phone_login.html", form=form)

@app.route("/chat")
def chat():
    """Redirects user to an existing chat or creates a new one."""
    if "user_id" not in session:
        return redirect(url_for("phone_login"))

    user = User.query.get(session["user_id"])
    
    if not user:
        flash("User not found! Please log in again.", "danger")
        session.clear()
        return redirect(url_for("phone_login"))

    # Find an existing chat
    chat = Chat.query.filter((Chat.user1_id == user.id) | (Chat.user2_id == user.id)).first()


@app.route("/chat/<int:receiver_id>")
def chat_with_user(receiver_id):
    """Chat with a specific user."""
    if "user_id" not in session:
        return redirect(url_for("phone_login"))

    user = User.query.get(session["user_id"])

    if not user:
        flash("User not found! Please log in again.", "danger")
        session.clear()
        return redirect(url_for("phone_login"))

    receiver = User.query.get(receiver_id)

    if not receiver:
        flash("Receiver not found!", "danger")
        return redirect(url_for("chat"))  # ✅ Redirect to a safe fallback

    return render_template("chat.html", user=user, receiver=receiver)

@app.route("/send_message/<int:receiver_id>", methods=["POST"])
def send_message(receiver_id):
    """Handles sending messages between users."""
    if "user_id" not in session:
        return redirect(url_for("phone_login"))

    user = User.query.get(session["user_id"])
    receiver = User.query.get(receiver_id)

    if not receiver:
        flash("Receiver not found!", "danger")
        return redirect(url_for("chat"))

    # Get the message from the form
    message_text = request.form.get("message")

    if message_text:
        flash("Message sent successfully!", "success")
        # TODO: Save the message to the database when chat storage is implemented

    return redirect(url_for("chat_with_user", receiver_id=receiver.id))

# Logout Route
@app.route("/logout")
def logout():
    """Logs out the user and clears session."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@socketio.on("send_message")
def handle_message(data):
    sender_id = session.get("user_id")
    receiver_id = data["receiver_id"]
    message_text = data["message"]

    if sender_id and receiver_id and message_text:
        message = Message(sender_id=sender_id, receiver_id=receiver_id, message=message_text)
        db.session.add(message)
        db.session.commit()

        emit("receive_message", {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message_text
        }, broadcast=True)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database is created before running
    app.run(debug=True)
    socketio.run(app, debug=True)

