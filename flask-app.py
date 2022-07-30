"""
2022.07.16: Teleporter Dormancy Module: Flask-App
1. Build a csv that contains staff-specific data
2. Build a username_password dictionary from the csv
3. Create a terminal app with working logic
4. Design frontend elements
5. Build frontend-backend integration with Flask
"""
import os
import sys
import uuid
import time
import pandas as pd
from flask import Flask, render_template, request, send_from_directory, send_file
from static.game_session import GameSession

"""
staff data load:
"""
staff_df = pd.read_csv('data/staff.csv')
# mission staff; dataframe
mission_staff = staff_df\
                    .loc[staff_df['involvedinmission'] == True]\
                    .astype({'order': int})\
                    .sort_values(by='order')

# initialize GameSession
gs = GameSession(mission_staff)

# Initialize Flask app:
app = Flask(__name__)

# display intro page
@app.route('/', methods=['GET', 'POST'])
def intro():
    """
    basic game storyline
    """
    return render_template('intro.html')

# display teleporter dormancy module
@app.route('/teleporter_dormancy_module', methods=['GET', 'POST'])
def module_home():
    """
    init Teleporter Dormancy Module UI
    """
    # reset GameSession attributes
    gs.reset_session()
    print(gs.lightpanel)
    return render_template('staff_validation_portal.html',
                            SessionUuid=gs.game_session_id,
                            CurrentLevel=gs.current_level,
                            StaffId=gs.get_current_staff_id(),
                            LightPanel=gs.lightpanel,
                            TerminalStateAchieved=False,
                            GameLost=False,
                            GameWon=False)

# validate the username/password credentials for each level
@app.route('/validate_credentials', methods=['GET', 'POST'])
def module_validate():
    """
    perform validation checks and advance game
    """
    # validate level
    guess_username = request.form.get('guess_username')
    guess_password = request.form.get('guess_password')
    guess = {'username': guess_username, 'password': guess_password}
    print(guess)
    # display message
    session_status = gs.validate_level(gs.current_level, guess)
    display_message = session_status.get('message')
    # tracks whether game has ended (either lost or won)
    terminal_state_achieved = True if session_status.get('verdict') != 'play' else False
    game_lost = True if session_status.get('verdict') == 'lost' else False
    game_won = True if session_status.get('verdict') == 'won' else False
    print(gs.lightpanel)
    return render_template('staff_validation_portal.html',
                            SessionUuid=gs.game_session_id,
                            CurrentLevel=gs.current_level,
                            StaffId=gs.get_current_staff_id(),
                            LightPanel=gs.lightpanel,
                            DisplayMessage=display_message,
                            TerminalStateAchieved=terminal_state_achieved,
                            GameLost=game_lost,
                            GameWon=game_won)

# display epilogue when game is successfully completed
@app.route('/epilogue', methods=['GET', 'POST'])
def show_epilogue():
    """
    display a pdf showing a newspaper clipping. This is the epilogue of the game.
    """
    pdf_rel_filepath = 'static/images/epilogue.pdf'
    
    return send_file(open(pdf_rel_filepath, 'rb'), download_name='epilogue.pdf', mimetype='application/pdf')

"""
app testing ground:
"""
if __name__ == '__main__':
    app.run(debug=True)
