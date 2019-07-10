import datetime
from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
from sqlalchemy import or_, and_


db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)

    message = {'data':data}
    return Response(json.dumps(message, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"

@app.route('/users', methods = ['POST'])
def create_user():
    c = json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "User Message"

#-------------------MESSAGE---------------------------------------------------------------------------------

@app.route('/messages', methods = ['POST'])
def create_message():
    body = request.get_json(silent=True)
    sessiondb = db.getSession(engine)
    content = body['content']
    user_from_id = body['user_from_id']
    user_to_id = body['user_to_id']

    user_from = sessiondb.query(entities.User).filter(entities.User.id == user_from_id).first()
    user_to = sessiondb.query(entities.User).filter(entities.User.id == user_to_id).first()

    message = entities.Message(
        content = content,
        user_from = user_from,
        user_to = user_to,
        sent_on = datetime.datetime.utcnow()
    )

    sessiondb.add(message)
    sessiondb.commit()

    return Response(json.dumps({'response':True}, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/messages/<id>', methods = ['GET'])
def get_message(id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        js = json.dumps(message, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/messages', methods = ['GET'])
def get_messages():
    sessiondb = db.getSession(engine)
    messages = sessiondb.query(entities.Message)
    response = []

    for message in messages:
        response.append(message)

    return Response(json.dumps({'data': response}, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c = json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    return 'Updated Message'

@app.route('/messages', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    message = session.query(entities.Message).filter(entities.Message.id == id).one()
    session.delete(message)
    session.commit()
    return "Deleted Message"

@app.route('/messages/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_messages_from_to(user_from_id, user_to_id ):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_from_id).filter(
        entities.Message.user_to_id == user_to_id
    )

    data = []
    for message in messages:
        data.append(message)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/authenticate', methods = ["POST"])
def authenticate():
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    #2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username == username
            ).filter(entities.User.password == password
            ).one()
        session['logged_user'] = user.id
        message = {'message': 'Authorized', 'user_id':user.id, 'username':user.username}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=401, mimetype='application/json')

@app.route('/current', methods = ["GET"])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']
        ).first()
    return Response(json.dumps(
            user,
            cls=connector.AlchemyEncoder),
            mimetype='application/json'
        )

@app.route('/logout', methods = ["GET"])
def logout():
    session.clear()
    return 'index.html'

@app.route('/chats/<user_from_id>/<user_to_id>', methods = ['GET'])
def getChats(user_from_id, user_to_id ):
    db_session = db.getSession(engine)
    chats = db_session.query(entities.Message).filter(
        or_(
            and_(entities.Message.user_from_id == user_from_id, entities.Message.user_to_id == user_to_id),
            and_(entities.Message.user_from_id == user_to_id, entities.Message.user_to_id == user_from_id)
        )
    )

    data = []
    for chat in chats:
        data.append(chat)

    return Response(json.dumps({'response':data}, cls=connector.AlchemyEncoder), mimetype='application/json')

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=5000, threaded=True, host=('127.0.0.1'))
