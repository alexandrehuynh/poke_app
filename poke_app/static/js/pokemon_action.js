document.addEventListener('DOMContentLoaded', function() {
    // Call function to update Pokémon count on page load
    updatePokemonCount();

    // Limit move selection to 4
    const movesSelect = document.getElementById('moves');
    if (movesSelect) {
        movesSelect.addEventListener('change', function() {
            let selectedOptions = Array.from(movesSelect.options).filter(option => option.selected);
            if (selectedOptions.length > 4) {
                alert('You can select up to 4 moves.');
                // Deselect the last selected option if more than 4 are selected
                selectedOptions[selectedOptions.length - 1].selected = false;
            }
        });
    }
});

// Function to update Pokémon count
function updatePokemonCount() {
    fetch('/pokemon_count')  // Assume you have a Flask route that returns the current count
        .then(response => response.json())
        .then(data => {
            const countElement = document.getElementById('pokemon-count');
            if (countElement) {
                countElement.textContent = `Total # of Pokémon: ${data.count}`;
            }
            // Update other UI elements as needed based on the count
        })
        .catch(error => console.error('Error fetching Pokémon count:', error));
}
