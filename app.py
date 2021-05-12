from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from database import User, Message

app = Flask(__name__)
engine = create_engine("sqlite:///messenger.db")
session = sessionmaker(engine)
db = session()


@app.teardown_appcontext
def close_db(error):
    db.close()
    engine.dispose()


@app.route('/user', methods=['POST'])
def add_user():
    new_user_data = request.get_json()

    name = new_user_data['name']
    email = new_user_data['email']
    hashed_password = generate_password_hash(new_user_data['password'], method="sha256")

    existing_user = db.query(User).filter_by(email=email).first()

    if existing_user:
        return jsonify({'message': "User with this email already exists!"})

    new_user = User(name=name, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()

    user_result = db.query(User).filter_by(email=email).first()

    return jsonify({'user_id': user_result.user_id,
                    'name': user_result.name,
                    'email': user_result.email,
                    'password': user_result.password})


@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = db.query(User).all()

    return_users = []

    for user in all_users:
        user_dict = {}
        user_dict['user_id'] = user.user_id
        user_dict['name'] = user.name
        user_dict['email'] = user.email
        user_dict['password'] = user.password

        return_users.append(user_dict)

    return jsonify({'users': return_users})


@app.route('/user/<user_id>', methods=['GET'])
def get_one_user(user_id):
    user = db.query(User).filter_by(user_id=user_id).first()

    if user:
        return jsonify({'user_id': user.user_id,
                        'name': user.name,
                        'email': user.email,
                        'password': user.password})

    return jsonify({'message': 'user not found'})


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    user_to_update = db.query(User).filter_by(user_id=user_id).first()

    new_user_data = request.get_json()

    name = new_user_data['name']
    email = new_user_data['email']
    hashed_password = generate_password_hash(new_user_data['password'], method="sha256")

    user_to_update.name = name
    user_to_update.email = email
    user_to_update.password = hashed_password
    db.commit()

    updated_user = db.query(User).filter_by(user_id=user_id).first()

    return jsonify({'user_id': updated_user.user_id,
                    'name': updated_user.name,
                    'email': updated_user.email,
                    'password': updated_user.password})


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    db.query(User).filter_by(user_id=user_id).delete()
    db.commit()
    return jsonify({'message': 'the user is deleted'})


@app.route('/user/<user_id>/message', methods=['POST'])
def write_message(user_id):
    new_message_data = request.get_json()

    receiver = new_message_data['receiver']
    message = new_message_data['message']
    subject = new_message_data['subject']

    new_message = Message(sender=user_id, receiver=receiver,
                          message=message, subject=subject)
    db.add(new_message)
    db.commit()

    message_result = db.query(Message).filter_by(sender=user_id).first()

    return jsonify({'message_id': message_result.message_id,
                    'sender': message_result.sender,
                    'receiver': message_result.receiver,
                    'message': message_result.message,
                    'subject': message_result.subject,
                    'create_date': message_result.create_date,
                    'read': message_result.read
                    })


@app.route('/user/<user_id>/message', methods=['GET'])
def get_all_messages(user_id):
    all_messages = db.query(Message).filter(or_(Message.sender==user_id, Message.receiver==user_id)).all()

    if len(all_messages) == 0:
        return jsonify({'message': 'This user doesn\'t have messages yet.'})

    return_messages = []

    for message in all_messages:
        message_dict = {}
        message_dict['message_id'] = message.message_id
        message_dict['sender'] = message.sender
        message_dict['receiver'] = message.receiver
        message_dict['message'] = message.message
        message_dict['subject'] = message.subject
        message_dict['create_date'] = message.create_date
        message_dict['read'] = message.read

        return_messages.append(message_dict)

    return jsonify({'messages': return_messages})


@app.route('/user/<user_id>/message/unread', methods=['GET'])
def get_unread_messages(user_id):
    unread_messages = db.query(Message) \
        .filter(or_(receiver=user_id)) \
        .filter(read=False).all()

    return_messages = []

    for message in unread_messages:
        message_dict = {}
        message_dict['message_id'] = message.message_id
        message_dict['sender'] = message.sender
        message_dict['receiver'] = message.receiver
        message_dict['message'] = message.message
        message_dict['subject'] = message.subject
        message_dict['create_date'] = message.create_date
        message_dict['read'] = message.read

        return_messages.append(message_dict)

    return jsonify({'messages': return_messages})


@app.route('/user/<user_id>/message/<message_id>', methods=['GET'])
def get_one_message(user_id, message_id):
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


@app.route('/user/<user_id>/message/<message_id>', methods=['PUT'])
def read_message(user_id, message_id):
    message_to_read = db.query(Message).filter_by(message_id=message_id).first()

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


@app.route('/user/<user_id>/message/<message_id>', methods=['DELETE'])
def delete_message(user_id, message_id):
    db.query(Message).filter_by(message_id=message_id).delete()
    db.commit()
    return jsonify({'message': 'the message is deleted'})


if __name__ == 'main':
    app.run(debug=True)
