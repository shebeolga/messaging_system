from flask import Flask, request, jsonify, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from database import User, Message
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
engine = create_engine("sqlite:///messenger.db")
db_session = sessionmaker(engine)
db = db_session()


@app.teardown_appcontext
def close_db(error):
    db.close()
    engine.dispose()


def get_current_user():
    result = None

    if "user" in session:
        user = session["user"]
        result = db.query(User).filter_by(user_id=user).first()

    return result


@app.route('/register', methods=['POST'])
def register():
    user = get_current_user()

    if user:
        return jsonify({"message": "The user is already logged in"})

    new_user_data = request.get_json()

    name = new_user_data['name']
    email = new_user_data['email']
    hashed_password = generate_password_hash(new_user_data['password'], method="sha256")

    existing_user = db.query(User).filter_by(email=email).first()

    if existing_user:
        return jsonify({'message': "User with this email already exists"})

    new_user = User(name=name, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()

    user_result = db.query(User).filter_by(email=email).first()

    session["user"] = str(user_result.user_id)

    return jsonify({'user_id': user_result.user_id,
                    'name': user_result.name,
                    'email': user_result.email,
                    'password': user_result.password})


@app.route('/login', methods=['POST'])
def login():
    user = get_current_user()

    if user:
        return jsonify({"message": "The user is already logged in"})

    login_user_data = request.get_json()

    email = login_user_data['email']
    existing_user = db.query(User).filter_by(email=email).first()

    if existing_user:
        if check_password_hash(existing_user.password, login_user_data['password']):
            session["user"] = str(existing_user.user_id)
            return jsonify({'user': {'user_id': existing_user.user_id,
                                     'name': existing_user.name,
                                     'email': existing_user.email,
                                     'password': existing_user.password
                                     }})
        else:
            return jsonify({'message': 'The password is wrong'})
    else:
        return jsonify({'message': 'The user not found'})


@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "The user logged out"})


@app.route('/message', methods=['POST'])
def write_message():
    user = get_current_user()

    if not user:
        return jsonify({"message": "You have to login or register"})

    new_message_data = request.get_json()

    receiver = new_message_data['receiver']
    message = new_message_data['message']
    subject = new_message_data['subject']

    if str(receiver) == user.user_id:
        return jsonify({'message': 'You cannot write letters to yourself'})

    existing_receiver = db.query(User).filter_by(user_id=receiver).first()
    if not existing_receiver:
        return jsonify({'message': 'There is no such receiver in the system'})

    if len(message) == 0:
        return jsonify(({'message': 'You have to write something in your message'}))

    new_message = Message(sender=user.user_id, receiver=receiver,
                          message=message, subject=subject)
    db.add(new_message)
    db.commit()

    message_result = db.query(Message).filter_by(sender=user.user_id).first()

    return jsonify({'message': {'message_id': message_result.message_id,
                                'sender': message_result.sender,
                                'receiver': message_result.receiver,
                                'message': message_result.message,
                                'subject': message_result.subject,
                                'create_date': message_result.create_date,
                                'read': message_result.read
                                }})


@app.route('/message', methods=['GET'])
def get_all_messages():
    user = get_current_user()

    if not user:
        return jsonify({"message": "You have to login or register"})

    all_messages = db.query(Message) \
        .filter(or_(Message.sender == user.user_id, Message.receiver == user.user_id)).all()

    if len(all_messages) == 0:
        return jsonify({'message': 'You don\'t have messages yet'})

    return_messages = []

    for message in all_messages:
        message_dict = {'message_id': message.message_id,
                        'sender': message.sender,
                        'receiver': message.receiver,
                        'message': message.message,
                        'subject': message.subject,
                        'create_date': message.create_date,
                        'read': message.read
                        }

        return_messages.append(message_dict)

    return jsonify({'messages': return_messages})


@app.route('/message/unread', methods=['GET'])
def get_unread_messages():
    user = get_current_user()

    if not user:
        return jsonify({"message": "You have to login or register"})

    unread_messages = db.query(Message) \
        .filter(Message.receiver == user.user_id) \
        .filter(Message.read == False).all()

    if len(unread_messages) == 0:
        return jsonify({'message': 'You don\'t have unread messages'})

    return_messages = []

    for message in unread_messages:
        message_dict = {'message_id': message.message_id,
                        'sender': message.sender,
                        'receiver': message.receiver,
                        'message': message.message,
                        'subject': message.subject,
                        'create_date': message.create_date,
                        'read': message.read}

        return_messages.append(message_dict)

    return jsonify({'messages': return_messages})


@app.route('/message/<message_id>', methods=['GET'])
def get_one_message(message_id):
    user = get_current_user()

    if not user:
        return jsonify({"message": "You have to login or register"})

    message = db.query(Message).filter_by(message_id=message_id).first()

    if message:
        return jsonify({'message': {'message_id': message.message_id,
                                    'sender': message.sender,
                                    'receiver': message.receiver,
                                    'message': message.message,
                                    'subject': message.subject,
                                    'create_date': message.create_date,
                                    'read': message.read
                                    }})

    return jsonify({'message': 'The message not found'})


@app.route('/message/<message_id>', methods=['PUT'])
def read_message(message_id):
    user = get_current_user()

    if not user:
        return jsonify({'message': 'You have to login or register'})

    message_to_read = db.query(Message).filter_by(message_id=message_id).first()

    if message_to_read:
        if message_to_read.read:
            return jsonify({'message': 'You already read this message'})
        else:
            message_to_read.read = True
            db.commit()

            message = db.query(Message).filter_by(message_id=message_id).first()

            return jsonify({'message': {'message_id': message.message_id,
                                        'sender': message.sender,
                                        'receiver': message.receiver,
                                        'message': message.message,
                                        'subject': message.subject,
                                        'create_date': message.create_date,
                                        'read': message.read
                                        }})

    return jsonify({'message': 'There is no such message'})


@app.route('/message/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    user = get_current_user()

    if not user:
        return jsonify({"message": "You have to login or register"})

    message_to_delete = db.query(Message).filter_by(message_id=message_id).first()

    if not message_to_delete:
        return jsonify({'message': 'There is no such message'})

    db.query(Message).filter_by(message_id=message_id).delete()
    db.commit()

    return jsonify({'message': 'The message is deleted'})


if __name__ == 'main':
    app.run(debug=True)
