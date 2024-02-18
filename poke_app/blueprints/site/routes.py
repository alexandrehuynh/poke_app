from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask import request, redirect, url_for, render_template, flash
from flask_login import current_user, login_required
from ...models import db, Pokemon  # Make sure this import reflects your project structure
from ...helpers import get_pokemon_data, get_pokemon_moves  # Again, make sure this import is correct



#need to instantiate our Blueprint class
site = Blueprint('site', __name__, template_folder='site_templates' )


#use site object to create our routes
@site.route('/')
def pokecenter():
    if current_user.is_authenticated:
        # This line should fetch only the Pokémon that belong to the current user
        user_pokemons = current_user.pokemons.all()  # Assuming you have a 'pokemons' relationship set up
        return render_template('pokecenter.html', pokemons=user_pokemons)
    else:
        # Handle the case for when no user is logged in
        return render_template('pokecenter.html')
    
@site.route('/add_pokemon', methods=['GET', 'POST'])
def add_pokemon():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']
        sprite_type = request.form['sprite_type']
        
        pokemon_data = get_pokemon_data(pokemon_name)
        if pokemon_data and 'error' not in pokemon_data:
            # Choose the sprite based on user selection
            sprite_url = pokemon_data['shiny_sprite_url'] if sprite_type == 'shiny' else pokemon_data['default_sprite_url']
            
            new_pokemon = Pokemon(
                pokemon_name=pokemon_data['name'],
                image_url=sprite_url,
                type=','.join(pokemon_data['types']),
                abilities=','.join(pokemon_data['abilities']),
                user_id=current_user.get_id()
            )            
            db.session.add(new_pokemon)
            db.session.commit()
            flash('Pokemon added successfully.', 'success')
        else:
            flash(f"Could not find Pokémon named {pokemon_name}.", 'error')
            return redirect(url_for('site.add_pokemon'))

        
        return redirect(url_for('site.pokecenter'))

    return render_template('add_pokemon.html')

@site.route('/train_pokemon/<string:pokemon_id>', methods=['GET', 'POST'])
@login_required
def train_pokemon(pokemon_id):
    print("Training Pokémon ID:", pokemon_id)

    pokemon = Pokemon.query.get_or_404(pokemon_id)
    
    if request.method == 'POST':
        selected_moves = request.form.getlist('moves')
        if len(selected_moves) > 4:
            flash("You can select up to 4 moves.", "error")
            return redirect(url_for('site.train_pokemon', pokemon_id=pokemon.poke_id))
        
        # Assuming you have a method or process to save these moves
        pokemon.update_moves(selected_moves)
        db.session.commit()
        flash("Moves updated successfully.", "success")
        return redirect(url_for('site.pokecenter'))

    moves = get_pokemon_moves(pokemon.pokemon_name)
    return render_template('train_pokemon.html', pokemon=pokemon, moves=moves)

@site.route('/delete_pokemon/<string:pokemon_id>', methods=['POST'])
@login_required
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.filter_by(poke_id=pokemon_id).first()
    if pokemon:
        db.session.delete(pokemon)
        db.session.commit()
        flash('Pokémon released successfully.', 'success')
    else:
        flash('Pokémon not found.', 'error')
    return redirect(url_for('site.pokecenter'))

@site.route('/pokemon_count')
def pokemon_count():
    count = current_user.pokemons.count()
    return jsonify({'count': count})

