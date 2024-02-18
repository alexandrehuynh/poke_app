from flask import Blueprint, request, redirect, url_for, flash
from flask import request, redirect, url_for, render_template, flash
from flask_login import current_user, login_required
from ...models import db, Pokemon  # Make sure this import reflects your project structure
from ...helpers import get_pokemon_data, get_pokemon_moves  # Again, make sure this import is correct



#need to instantiate our Blueprint class
site = Blueprint('site', __name__, template_folder='site_templates' )


#use site object to create our routes
@site.route('/')
def pokecenter():
    all_pokemon = Pokemon.query.all()  # Query all Pokémon from the database
    return render_template('pokecenter.html', all_pokemon=all_pokemon)

@site.route('/add_pokemon', methods=['GET', 'POST'])
def add_pokemon():
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        pokemon_data = get_pokemon_data(pokemon_name)

        if pokemon_data and 'error' not in pokemon_data:
            # Here we create a new Pokemon instance using the fetched data
            new_pokemon = Pokemon(
                pokemon_name=pokemon_data['name'],
                image_url=pokemon_data['shiny_sprite_url'],
                description='A cool Pokémon',  # Replace with actual description if available
                type=','.join(pokemon_data['types']),  # Joining list of types into a single string
                abilities=','.join(pokemon_data['abilities']),  # Same for abilities
                user_id=current_user.get_id()  # Assuming you're using Flask-Login to get the current user's ID
            )
            db.session.add(new_pokemon)
            db.session.commit()
            flash('Pokemon added successfully.', 'success')
        else:
            flash(f"Could not find Pokémon named {pokemon_name}.", 'error')
        
        return redirect(url_for('site.pokecenter'))

    return render_template('add_pokemon.html')  # Render the page with the form if GET request or if POST fails


@site.route('/train_pokemon/<pokemon_name>', methods=['GET', 'POST'])
@login_required
def train_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    
    if request.method == 'POST':
        selected_moves = request.form.getlist('moves')
        if len(selected_moves) > 4:
            flash("You can select up to 4 moves.", "error")
            return redirect(url_for('site.train_pokemon', pokemon_id=pokemon.id))
        
        # Assuming you have a method or process to save these moves
        pokemon.update_moves(selected_moves)
        db.session.commit()
        flash("Moves updated successfully.", "success")
        return redirect(url_for('site.pokecenter'))

    moves = get_pokemon_moves(pokemon.name)
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

