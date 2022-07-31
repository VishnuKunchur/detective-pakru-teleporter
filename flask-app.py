"""
flask app for running Teleporter game
"""

import os
import sys
import time
import pandas as pd
from flask import Flask, render_template, request, send_file, session

"""
staff data load:
"""
staff_df = pd.read_csv('data/staff.csv')
# mission staff; dataframe
mission_staff_credentials = staff_df\
                                .loc[staff_df['involvedinmission'] == True]\
                                .astype({'order': int})\
                                [['order', 'username', 'password']]\
                                .sort_values(by='order')\
                                .set_index('order').T.to_dict()

app = Flask(__name__)
app.secret_key = 'kavyakantharemakanthakurupsindhu'

"""
game session methods:
"""



"""
#######################################################################################################
APP ROUTES
#######################################################################################################
"""

# display intro page
@app.route('/', methods=['GET', 'POST'])
def intro():
    """
    basic game storyline
    """
    session['max_level'] = 5

    def init_lightpanel():
        """
        initialize lightpanel for UI display on Teleporter Dormancy Module
        """
        lightpanel_colorclass_dict = {}
        for idx in range(1, session['max_level'] + 1):
            lightpanel_colorclass_dict[idx] = 'circle-inactive'
        return lightpanel_colorclass_dict

    session['current_level'] = 1
    session['num_attempts_level'] = 0
    session['max_attempts_level'] = 3
    session['rem_attempts_level'] = session['max_attempts_level'] - session['num_attempts_level']
    session['verdict'] = 'play'
    session['lightpanel'] = init_lightpanel()
    session['message'] = ''
    session['terminal_state_achieved'] = False
    session['game_lost'] = False
    session['game_won'] = False

    return render_template('intro.html')

# username/password validation:
@app.route('/validate_credentials', methods=['GET', 'POST'])
def validate_credentials():
    """
    execute game dynamics; validate credentials for each level
    """
    current_level = session['current_level']
    truth = mission_staff_credentials[current_level]
    true_username = truth.get('username')
    true_password = truth.get('password')
    print('TRUE CREDENTIALS: ', true_username, true_password)

    # validate supplied username/password
    if request.method == 'POST':
        # reading user input
        guess_username = request.form.get('guess_username')
        guess_password = request.form.get('guess_password')
        # cleaning guess_password text
        guess_password = guess_password.replace('\n', '').replace(' ', '')

        print(guess_username, guess_password)

        # username invalid:
        if true_username != guess_username:
            session['lightpanel'][str(current_level)] = 'circle-red'
            session['message'] = 'INCORRECT USERNAME ENTERED. SUSPICIOUS ROGUE ACTIVITY DETECTED. TELEPORTER WILL NOW TERMINATE.'
            session['verdict'] = 'lost'
            return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=True,
                                DisplayMessage=session['message'],
                                GameLost=True,
                                GameWon=False)

        # password invalid:
        elif true_password != guess_password:
            session['num_attempts_level'] += 1
            session['rem_attempts_level'] = session['max_attempts_level'] - session['num_attempts_level']
            if session['rem_attempts_level'] > 0:
                session['lightpanel'][str(current_level)] = 'circle-yellow'
                session['message'] = 'INCORRECT USERNAME/PASSWORD COMBINATION. {} ATTEMPTS REMAINING.'.format(session['rem_attempts_level'])
                return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=False,
                                DisplayMessage=session['message'],
                                GameLost=False,
                                GameWon=False)
            else:
                session['lightpanel'][str(current_level)] = 'circle-red'
                session['message'] = 'TOO MANY ATTEMPTS. SUSPICIOUS ROGUE ACTIVITY DETECTED. TELEPORTER WILL NOW TERMINATE.'
                session['verdict'] = 'lost'
                return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=True,
                                DisplayMessage=session['message'],
                                GameLost=True,
                                GameWon=False)
        
        # both username and password are valid:
        else:
            session['lightpanel'][str(session['current_level'])] = 'circle-green'
            session['current_level'] += 1
            session['num_attempts_level'] = 0
            session['rem_attempts_level'] = session['max_attempts_level'] - session['num_attempts_level']
            if session['current_level'] > session['max_level']:
                # win game:
                # this is to prevent index errors when querying the credentials dictionary.
                session['current_level'] = session['max_level']
                session['message'] = 'VALIDATION COMPLETE. ATTEMPTING TO SWITCH TELEPORTER INTO ACTIVE MODE..'
                session['verdict'] = 'won'
            
                return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=True,
                                DisplayMessage=session['message'],
                                GameLost=False,
                                GameWon=True)
            else:
                # advance level
                session['message'] = 'VALIDATION SUCCESSFUL FOR {}'.format(true_username.upper())
                return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=False,
                                DisplayMessage=session['message'],
                                GameLost=False,
                                GameWon=False)
    # plain GET
    else:
        return render_template('staff_validation_portal.html',
                                LightPanel=session['lightpanel'],
                                CurrentLevel=session['current_level'],
                                TerminalStateAchieved=False,
                                DisplayMessage=session['message'],
                                GameLost=False,
                                GameWon=False)

# display epilogue:
@app.route('/epilogue', methods=['GET', 'POST'])
def show_epilogue():
    """
    display game epilogue
    """
    pdf_filepath = 'static/images/epilogue.pdf'

    return send_file(open(pdf_filepath, 'rb'), mimetype='application/pdf')


"""
run flask app
"""
if __name__ == '__main__':
    app.run(threaded=True, port=5000)
