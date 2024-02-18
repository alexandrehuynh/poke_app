from werkzeug.security import generate_password_hash #generates a unique password hash for extra security 
from flask_sqlalchemy import SQLAlchemy #this is our ORM (Object Relational Mapper)
from flask_login import UserMixin, LoginManager #helping us load a user as our current_user 
from datetime import datetime #put a timestamp on any data we create (Users, Products, etc)
import uuid #makes a unique id for our data (primary key)
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field





#instantiate all our classes
db = SQLAlchemy() #make database object
login_manager = LoginManager() #makes login object 
ma = Marshmallow() #makes marshmallow object


#use login_manager object to create a user_loader function
@login_manager.user_loader
def load_user(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id) #this is a basic query inside our database to bring back a specific User object

#think of these as admin (keeping track of what products are available to sell)
class User(db.Model, UserMixin): 
    #CREATE TABLE User, all the columns we create
    user_id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    pokemons = db.relationship('Pokemon', backref='trainer', lazy='dynamic')
    date_added = db.Column(db.DateTime, default=datetime.utcnow) #this is going to grab a timestamp as soon as a User object is instantiated


    #INSERT INTO User() Values()
    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email 
        self.password = self.set_password(password) 



    #methods for editting our attributes 
    def set_id(self):
        return str(uuid.uuid4()) #all this is doing is creating a unique identification token
    

    def get_id(self):
        return str(self.user_id) #UserMixin using this method to grab the user_id on the object logged in
    
    
    def set_password(self, password):
        return generate_password_hash(password) #hashes the password so it is secure (aka no one can see it)
    

    def __repr__(self):
        return f"<User: {self.username}>"
    
class Pokemon(db.Model):
    poke_id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    pokemon_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255))  # URL to the image
    moves = db.Column(db.String(255))  # Stores moves as a comma-separated string
    type = db.Column(db.String(50), nullable=False)
    abilities = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'))

    def set_moves(self, moves_list):
        """Set the Pokemon's moves from a list."""
        self.moves = ','.join(moves_list)

    def get_moves(self):
        """Get the Pokemon's moves as a list."""
        return self.moves.split(',') if self.moves else []
    
    # def update_moves(self, moves_list):
    #     """Update the Pokemon's moves.

    #     Args:
    #         moves_list (list): A list of move names to be saved.
    #     """
    #     # Join the list of moves into a comma-separated string and save
    #     self.moves = ','.join(moves_list)

    def __repr__(self):
        return f"<Pokemon: {self.pokemon_name}>"

class PokemonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pokemon
        sqla_session = db.session  # Provide the SQLAlchemy session
        load_instance = True  # Optional: for deserialization
        include_fk = True  # Include foreign keys in the serialization
        dump_only = ("poke_id",)  # Fields to exclude from deserialization

    pokemon_name = auto_field(required=True)
    image_url = auto_field(required=True)
    moves = auto_field()
    type = auto_field(required=True)
    abilities = auto_field(required=True)
    user_id = auto_field()   # Now included in both load and dump

    @validates('pokemon_name')
    def validate_pokemon_name(self, value):
        if len(value) < 1:
            raise ValidationError("Pokemon name must not be empty.")

    @post_load
    def make_pokemon(self, data, **kwargs):
        return Pokemon(**data)

# class PokemonSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Pokemon
#         sqla_session = db.session  # Ensure the SQLAlchemy session is provided
#         load_instance = True  # Deserialization will produce model instances
#         include_fk = True  # Include foreign keys in the serialization/deserialization

#     poke_id = auto_field(dump_only=True)  # Generated by the system, so it's only for dumping
#     pokemon_name = auto_field(required=True)
#     image_url = auto_field(required=True)
#     moves = auto_field()
#     type = auto_field(required=True)
#     abilities = auto_field(required=True)
#     user_id = auto_field()  # Included for both loading and dumping

#     @validates('pokemon_name')
#     def validate_pokemon_name(self, value):
#         if len(value) < 1:
#             raise ValidationError("Pokemon name must not be empty.")

# Instantiate our PokemonSchema class so we can use them in our application
pokemon_schema = PokemonSchema()  # For serializing a single Pokemon
pokemons_schema = PokemonSchema(many=True)  # For serializing multiple Pokemon
