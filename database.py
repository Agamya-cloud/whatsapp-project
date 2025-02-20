from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    qr_code = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(300), nullable=True) 
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()