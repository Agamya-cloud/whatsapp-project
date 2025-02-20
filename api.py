from flask import Blueprint, request, jsonify, session
from database import db, User, Message
import qrcode
import os
from api import api_bp

api_bp = Blueprint("api", __name__)

# Generate QR Code for login
@api_bp.route("/api/generate_qr", methods=["GET"])
def generate_qr():
    username = request.args.get("username", "testuser")
    qr_data = f"http://localhost:5000/api/authenticate/{username}"
    qr = qrcode.make(qr_data)
    qr_path = os.path.join("static", f"{username}_qr.png")
    qr.save(qr_path)

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, qr_code=qr_path)
        db.session.add(user)
    else:
        user.qr_code = qr_path

    db.session.commit()
    return jsonify({"qr_path": qr_path})

# Authenticate user via QR Code
@api_bp.route("/api/authenticate/<username>", methods=["GET"])
def authenticate(username):
    session["user"] = username
    return jsonify({"message": "Login successful", "username": username})

# Send message
@api_bp.route("/api/send_message", methods=["POST"])
def send_message():
    data = request.json
    sender = session.get("user")
    receiver = data.get("receiver")
    message = data.get("message")

    if not sender:
        return jsonify({"error": "User not authenticated"}), 401

    new_message = Message(sender=sender, receiver=receiver, content=message)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({"message": "Message sent successfully"})

# Fetch messages between two users
@api_bp.route("/api/get_messages", methods=["GET"])
def get_messages():
    sender = session.get("user")
    receiver = request.args.get("receiver")

    if not sender:
        return jsonify({"error": "User not authenticated"}), 401

    messages = Message.query.filter(
        ((Message.sender == sender) & (Message.receiver == receiver)) |
        ((Message.sender == receiver) & (Message.receiver == sender))
    ).all()

    return jsonify({"messages": [{"sender": m.sender, "receiver": m.receiver, "content": m.content} for m in messages]})
