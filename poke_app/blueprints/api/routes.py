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

    new_pokemon = Pokemon(
        pokemon_name=data.get('pokemon_name'),
        image_url=data.get('image_url'),
        moves=data.get('moves', ''),  # Default to empty string if not provided
        type=data.get('type'),
        abilities=data.get('abilities'),
        user_id=current_user.get_id()  # Link the Pokemon to the user
    )

    db.session.add(new_pokemon)
    try:
        db.session.commit()
        # Use PokemonSchema to serialize the new pokemon including the user_id
        pokemon_schema = PokemonSchema()
        response = pokemon_schema.dump(new_pokemon)
        # Add user_id to the response manually if it's not included by default
        response['user_id'] = new_pokemon.user_id
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/pokemon/train_moves/<pokemon_id>', methods=['PUT'])
@jwt_required()
def train_new_moves(pokemon_id):
    data = request.json
    new_moves = data.get('moves')  # Expected to be a list of move names
    
    # Fetch the Pokémon by ID
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        return jsonify({'error': 'Pokémon not found'}), 404
    
    # Validate moves (optional, could be added here)
    
    # Update the Pokémon's moves
    # Assuming you have a method in your Pokemon model to handle the moves update
    pokemon.set_moves(new_moves[:4])  # Limit to first 4 moves if more are provided
    
    # Save changes to the database
    try:
        db.session.commit()
        return jsonify({'message': 'Pokémon moves trained successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500