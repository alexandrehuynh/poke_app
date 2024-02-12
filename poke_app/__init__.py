from flask import Flask 
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_jwt_extended import JWTManager 


# internal imports
from config import Config 
from .models import login_manager, db
from .blueprints.site.routes import site #importing blueprint object
from .blueprints.auth.routes import auth
# from .blueprints.api.routes import api
from .helpers import JSONEncoder 



#instantiate our Flask app
app = Flask(__name__) #is passing in the name of our directory as the name of our app

#going to tell our app what Class to look to for configuration
app.config.from_object(Config)
jwt = JWTManager(app) # allows our app to use JWTMaanager from anywhere 


# wrap our whole app in our login_manager so we can use it wherever in our app
login_manager.init_app(app)
login_manager.login_view = 'auth.sign_id' #authentication route 
login_manager.login_message = 'Hey you! Login Please' 
login_manager.login_message_category = 'warning'


app.register_blueprint(site) #pass in site blueprint object to register
app.register_blueprint(auth)
# app.register_blueprint(api)


# intantiate our database & wrap our app in it
db.init_app(app)
migrate = Migrate(app, db) #things we are connecting/migrating (our application to our database)
app.json_encoder = JSONEncoder # we are not instantiating this but rather poitning to this class 
cors = CORS(app) #Cross Origin Resource Sharing aka allowing other apps to talk to our API