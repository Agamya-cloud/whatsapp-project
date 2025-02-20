from flask import Blueprint, render_template
from flask_socketio import emit
from flask_login import login_required
from app import socketio, db
from models import Message

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chatroom():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    msg = Message(sender=data['sender'], receiver=data['receiver'], message=data['message'])
    db.session.add(msg)
    db.session.commit()
    
    emit('message', data, broadcast=True)
