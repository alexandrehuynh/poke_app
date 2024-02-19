from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_login import current_user, login_required
from marshmallow import ValidationError

# internal import
from poke_app.models import User, Pokemon, PokemonSchema, db, pokemon_schema, pokemons_schema


api = Blueprint('api', __name__, url_prefix='/api') # every route needs to be preceeded with /api

@api.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_list = [{"user_id": user.user_id, "username": user.username} for user in users]
    return jsonify(users_list), 200

@api.route('/token', methods=['POST'])
def token():
    data = request.get_json()
    if data and 'user_id' in data:
        user_id = data['user_id']
        user = User.query.get(user_id)
        if user:
            access_token = create_access_token(identity=user_id)
            return {'status': 200, 'access_token': access_token}
        else:
            return {'status': 404, 'message': 'User not found'}
    return {'status': 400, 'message': 'Missing User ID. Try Again.'}

@api.route('/pokecenter')
@jwt_required()
def get_pokemon():
    # Assuming you're using Flask-JWT-Extended to handle JWTs
    current_user_id = get_jwt_identity()  # Retrieve the JWT identity, which should be the user_id

    # Query only the Pokémon that belong to the current user
    user_pokemons = Pokemon.query.filter_by(user_id=current_user_id).all()

    # Serialize the user's Pokémon using the schema
    response = pokemons_schema.dump(user_pokemons)
    return jsonify(response)


@api.route('/pokemon/create', methods=['POST'])
@jwt_required()
def create_pokemon():
    # Retrieve the current user's ID from the JWT
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # Check if the user already has 6 or more Pokémon
    if user and user.pokemons.count() >= 6:
        return jsonify({'error': 'You cannot have more than 6 Pokémon.'}), 400

    data = request.get_json()
    try:
        # Add user_id to data for linking the new Pokémon to the user
        data['user_id'] = current_user_id
        new_pokemon = pokemon_schema.load(data, session=db.session)
        db.session.add(new_pokemon)
        db.session.commit()
        return jsonify(pokemon_schema.dump(new_pokemon)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
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
    
@api.route('/pokemon/delete/<string:pokemon_id>', methods=['DELETE'])
@jwt_required()
def delete_pokemon(pokemon_id):
    current_user_id = get_jwt_identity()
    print(f"JWT Identity: {current_user_id}")

    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        return jsonify({'error': 'Pokémon not found'}), 404

    print(f"Pokémon Owner ID: {pokemon.user_id}")
    if str(pokemon.user_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized to delete this Pokémon'}), 403

    db.session.delete(pokemon)
    try:
        db.session.commit()
        return jsonify({'message': 'Pokémon deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500