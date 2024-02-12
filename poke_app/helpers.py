import decimal
import requests
import requests_cache
import json


# setup our api cache location (thhis will be a temporary database storing our api calls)
requests_cache.install_cache('image_cache', backend='sqlite')



def get_pokemon_data(pokemon_name):
    # The URL for the PokéAPI endpoint for a specific Pokémon
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'

    # Sending a GET request to the PokéAPI
    response = requests.get(url)

    # If the request was successful, we proceed
    if response.status_code == 200:
        data = response.json()
        # Extracting the name, abilities, types, base experience, and stats
        name = data.get('name', '').capitalize()
        abilities = [ability['ability']['name'] for ability in data.get('abilities', [])]
        types = [ptype['type']['name'] for ptype in data.get('types', [])]
        base_experience = data.get('base_experience', 0)
        stats = {stat['stat']['name']: stat['base_stat'] for stat in data.get('stats', [])}

        # Correcting the path to extract the shiny sprite URL
        shiny_sprite_url = data['sprites']['other']['home']['front_shiny']

        # Extracting moves - we'll only take the move name for simplicity
        moves = [move['move']['name'] for move in data.get('moves', [])]

        # Compile all the extracted data into a single dictionary
        pokemon_data = {
            'name': name,
            'abilities': abilities,
            'types': types,
            'base_experience': base_experience,
            'stats': stats,
            'shiny_sprite_url': shiny_sprite_url,
            'moves': moves,
        }
        return pokemon_data

    # Handle errors or cases where the Pokémon is not found
    else:
        return {'error': f'Pokémon {pokemon_name} not found.'}


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): #if the object is a decimal we are going to encode it 
                return str(obj)
        return json.JSONEncoder(JSONEncoder, self).default(obj) #if not the JSONEncoder from json class can handle it