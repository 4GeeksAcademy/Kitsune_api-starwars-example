"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person
import json

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ACÁ EMPIEZAN LOS ENDPOINTS


# endpoint para consultar todos los datos de una tabla
@app.route('/user', methods=['GET'])
def handle_hello():

    results = User.query.all()
    users_list = list(map(lambda item: item.serialize(),results))


    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "results": users_list
    }

    return jsonify(response_body), 200

# endpoint para consultar un dato en una tabla
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    print(id)

    user = User.query.filter_by(id=id).first()
  
    if user is None:
        return jsonify({"msg":"Usuario no existe"}), 404
    

    response_body = {
        "result": user.serialize()
    }

    return jsonify(response_body), 200


# endpoint para crear un dato en una tabla
@app.route('/user', methods=['POST'])
def create_user():

    body = json.loads(request.data)
    # json.loads(request.body.decode(encoding='UTF-8'))
    print(body)
    user = User(email=body["email"], password=body["password"], is_active=body["is_active"])
    db.session.add(user)
    db.session.commit()

    response_body = {
        "msg": "El usuario ha sido creado",
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
