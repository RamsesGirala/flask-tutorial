import os
import logging

from flask import Flask,request
import hmac
from hashlib import sha256
from . import db
from . import auth
from . import blog

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    
    app.register_blueprint(auth.bp)

    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    #add logger
    app.logger = logging.getLogger('my_logger')


    # a simple page that says hello
    @app.route('/hola')
    def hello():
        return 'Hello, World!'

    @app.route('/recieveJobUpdate', methods=["POST"])
    def recieveJobUpdate():
        app.logger.warn("--------------EJECUTANDO RECIEVE JOB UPDATE--------------")
        
        if request.headers.get('X-Signature-256') == None:
            return "NO VIENE DE CVAT, NO VIENE LA CLAVE"

        app.logger.warn(f"LA QUE LLEGA: {request.headers.get('X-Signature-256')}")

        signature = (
            "sha256="
            + hmac.new("secretforcvat".encode("utf-8"), request.data, digestmod=sha256).hexdigest()
        )

        app.logger.warn(f"LA QUE SE ESPERA: {signature}")

        if hmac.compare_digest(request.headers["X-Signature-256"], signature):
            app.logger.warn(request.json)
            return app.response_class(status=200)

        app.logger.warn(f"TYPE DEL JSON QUE NO VIENE DE CVAT: {type(request.json)}")
        app.logger.warn(f"JSON QUE NO VIENE DE CVAT: {request.json}")

        app.logger.warn(f"STATUS DEL JOB: {request.json['job']['state']}")
        if(request.json['job']['state'] == 'completed'):
            app.logger.warn("EL JOB ESTA COMPLETED")

        
        return "NO VIENE DE CVAT, CLAVES INCORRECTAS"

    return app