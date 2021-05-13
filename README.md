# Messaging system

The system is responsible for sending messages between users. It supporets user's registration, log in and log out, as well as writing, receivind, reading and deleting messages.

It's done on python with flask framework. Database support - with sqlalchemy modul.

## Deployment

On pythonwnywhere: <a href="https://www.pythonanywhere.com/user/shebeolga/">shebeolga.pythonanywhere.com</a>

## Database

Is written on SQLite3. Consists of two tables:

```
users
  user_id (integer) - primery key
  name  (string)
  email (string)
  password (string)
```

```
messages
  message_id (integer) - primery key
  sender (integer) - foreing key (users.user_id)
  receiver (integer) - foreing key (users.user_id)
  message (text)
  subject (string)
  create_date (datetime) - default now()
  read (boolean) - default false
```

## Routs

### Registration
POST ```http://shebeolga.pythonanywhere.com/register```

The body of the request must be JSON. Sample:
```
{
  "name": "username",
  "email": "useremail@fakemail.com",
  "passwrod": "password"
}
```
Valid request will return a json object:
```
{
    "user_id": 1,
    "name": "username",
    "email": "useremail@fakemail.com",
    "password": "sha256$0Bxm9Sk9108X3nRT$0775939f4475bfa79aaaa005cc143de50dc55ad8dbbd5db55f5bf5f95f6d2e64"
}
```
If a user with this email already exists, the response will be:
```
{
  "message": "User with this email already exists!"
}
```

### Login
POST ```http://shebeolga.pythonanywhere.com/login```

The body of the request must be JSON. Sample:
```
{
  "email": "useremail@fakemail.com",
  "passwrod": "password"
}
```
Valid request will return a json object:
```
{
    "user_id": 1,
    "name": "username",
    "email": "useremail@fakemail.com",
    "password": "sha256$0Bxm9Sk9108X3nRT$0775939f4475bfa79aaaa005cc143de50dc55ad8dbbd5db55f5bf5f95f6d2e64"
}
```
If there is no such user in database, the response will be:
```
{
  "message": "The user not found"
}
```
If the password is wrong, the response will be:
```
{
  "message": "The password is wrong"
}
```

### Logout
POST ```http://shebeolga.pythonanywhere.com/logout```

Removes user from current session.

### Write message
POST ```http://shebeolga.pythonanywhere.com/message```

The body of the request must be JSON. Sample:
```
{
  "receiver": 2,
  "message": "Some text",
  "subject": "Some string"
}
```
Valid request will return a json object:
```
{
    "message_id": 1,
    "sender": 1,
    "receiver": 2,
    "message": "Some text",
    "subject": "Some string",
    "create_date": 2021-05-12 13:00:00,
    "read": false
}
```
If there is no such receiver in database, the response will be:
```
{
  "message": "There is no such receiver in database"
}
```
If the message is empty, the response will be:
```
{
  "message": "You have to write something in your message"
}
```

### Get all messages
GET ```http://shebeolga.pythonanywhere.com/message```

The response will be the list of json objects with all messages that logged in user has.

If there are no messages, the response will be:
```
{
  "message": "You don't have messages yet"
}
```

### Get unread messages
GET ```http://shebeolga.pythonanywhere.com/message/unread```

The response will be the list of json objects with the messages that read = false.

If there are no unread messages, the response will be:
```
{
  "message": "You don't have unread messages"
}
```

### Get specific message
GET ```http://shebeolga.pythonanywhere.com/message/<message_id>```

The response will be the json object with the messages with provided id.

If there is no such message, the response will be:
```
{
  "message": "The message not found"
}
```

### Read message
PUT ```http://shebeolga.pythonanywhere.com/message/<message_id>```

During the processing of this request message.read = true.
The response will be the json object with the messages with provided id and new read value.

If there is no such message, the response will be:
```
{
  "message": "The message not found"
}
```
If the message is already read, the response will be:
```
{
  "message": "You've already read this message"
}
```

### Delete message
DELETE ```http://shebeolga.pythonanywhere.com/message/<message_id>```

Deletes the message with the given id.
The response will be:
```
{
  "message": "The message is deleted"
}
```
If there is no such message, the response will be:
```
{
  "message": "The message not found"
}
```
