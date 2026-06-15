from flask import Flask, render_template, request, jsonify, session
from gameFunctions import pullDatabase, pullAlltimePlayers, getNewPlayer, generateNewPlayer, retrieveMysteryPlayer
from unidecode import unidecode

app = Flask(__name__)
app.secret_key = "adsiaksjckans;ldfja;ie192wpqdfa;ksjdf3o" 

data = pullDatabase()


def generate_table(seasonValue, debutValue, retirementValue, teamValue):
    """Generate HTML table for a random player based on filters.

    Returns a tuple of (html_string, player_id) so the caller can
    store the player ID in the session rather than a global variable.
    """
    try:
        baseLink, chosenPlayerID = generateNewPlayer(
            data,
            seasonValue=seasonValue,
            debutValue=debutValue,
            retirementValue=retirementValue,
            teamValue=teamValue
        )

        df = getNewPlayer(baseLink)

        return df.to_html(index=False, classes="table table-striped"), chosenPlayerID

    except ValueError as e:
        return f"<p class='alert alert-warning'>{str(e)}</p>", None
    except Exception as e:
        print(f"Error generating table: {e}")
        return "<p class='alert alert-danger'>An error occurred. Please try again.</p>", None


@app.route('/')
def index():
    """Render the main page."""
    return render_template('layout.html')


@app.route('/generate_table')
def generate_table_route():
    # Get raw string values from request
    season_str = request.args.get("season", "")
    debut_str = request.args.get("debut", "")
    retirement_str = request.args.get("retirement", "")
    team_str = request.args.get("team", "")
    
    # Convert to appropriate types, handling empty strings
    try:
        season = int(season_str) if season_str.strip() else None
        debut = int(debut_str) if debut_str.strip() else None
        retirement = int(retirement_str) if retirement_str.strip() else None
        team = team_str.strip().upper() if team_str.strip() else None
    except ValueError:
        return "<p class='alert alert-danger'>Invalid filter values. Please enter valid numbers.</p>"
    
    html, player_id = generate_table(season, debut, retirement, team)
    if player_id is not None:
        session['last_player_id'] = player_id
    return html


@app.route('/reveal')
def reveal():
    """Return the current mystery player's name (used by Give Up)."""
    player_id = session.get('last_player_id')
    if player_id is None:
        return jsonify({"name": None, "message": "No player has been generated yet."})
    correct_name = retrieveMysteryPlayer(data, player_id)
    return jsonify({"name": correct_name, "message": f"The player was {correct_name}."})


@app.route('/check_guess', methods=['POST'])
def check_guess():
    # Ensure a player has been generated for this session
    player_id = session.get('last_player_id')
    if player_id is None:
        return jsonify({
            "correct": False,
            "message": "Please generate a player first!"
        })

    # Get user's guess from request
    data_json = request.get_json()
    if not data_json:
        return jsonify({
            "correct": False,
            "message": "Invalid request"
        })

    user_guess = data_json.get("guess", "").strip()

    if not user_guess:
        return jsonify({
            "correct": False,
            "message": "Please enter a guess!"
        })

    # Normalize the user's guess (remove accents, lowercase)
    normalized_guess = unidecode(user_guess).lower()

    # Retrieve the correct player name
    correct_name = retrieveMysteryPlayer(data, player_id)
    normalized_correct = unidecode(correct_name).lower()

    # Check if guess is correct
    if normalized_guess == normalized_correct:
        return jsonify({
            "correct": True,
            "message": f"Correct! The player is {correct_name}."
        })
    else:
        return jsonify({
            "correct": False,
            "message": "Incorrect guess, try again!"
        })


if __name__ == "__main__":
    # For production, use a proper WSGI server like gunicorn
    # and set debug=False
    app.run(debug=True, use_reloader=False)