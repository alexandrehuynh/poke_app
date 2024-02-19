from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required 
from flask_login import current_user, login_required
from marshmallow import ValidationError

# internal import
from poke_app.models import User, Pokemon, PokemonSchema, db, pokemon_schema, pokemons_schema


api = Blueprint('api', __name__, url_prefix='/api') # every route needs to be preceeded with /api


@api.route('/token', methods=['GET', 'POST'])
def token():
    
    data = request.json # building api requests no () 
    if data:
        client_id = data['client_id']
        access_token = create_access_token(identity=client_id)
        return {
            'status': 200,
            'access_token': access_token
        }
    else:
        return {
            'status': 400,
            'message': 'Missing Client Id. Try Again.'
        }
    
@api.route('/pokecenter')
@jwt_required()
def get_pokemon():

    #this is a list of objects
    allpokes = Pokemon.query.all()

    #since we cant send a list of objects through api calls we need to change them into dictionaries/jsonify them
    response = pokemons_schema.dump(allpokes) #loop through allpoke list of objects and change objects into dictionarys
    return jsonify(response)


@api.route('/pokemon/create', methods=['POST'])
@jwt_required()
def create_pokemon():
 
    data = request.get_json()
    print("Received Data:", data)  # Debug print

    # Load data into a Pokemon model instance
    try:
        new_pokemon = pokemon_schema.load(data, session=db.session)  # This will directly return a Pokemon instance
    except ValidationError as err:
        return jsonify(err.messages), 400

    print("Loaded Pokemon:", new_pokemon)  # Debug print to confirm loading is correct

    # Manually set the user_id if not set by load method
    if not new_pokemon.user_id:
        new_pokemon.user_id = current_user.get_id()

    db.session.add(new_pokemon)  # Add the new Pokemon model instance directly
    try:
        db.session.commit()
        return jsonify(pokemon_schema.dump(new_pokemon)), 201
    except Exception as e:
        db.session.rollback()
        print(e)  # Debug print the error
        return jsonify({'error': str(e)}), 500


@api.route('/pokemon/train_moves/<string:pokemon_id>', methods=['PUT'])
@jwt_required()
def train_moves(pokemon_id):
    data = request.json
    new_moves = data.get('moves')  # Expected to be a list of move names
    
    # Fetch the Pokémon by ID
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        return jsonify({'error': 'Pokémon not found'}), 404
    
    # Validate moves (optional, could be added here)
    
    # Update the Pokémon's moves
    pokemon.set_moves(new_moves[:4])  # Limit to first 4 moves if more are provided
    
    # Save changes to the database
    try:
        db.session.commit()
        return jsonify({'message': 'Pokémon moves trained successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500