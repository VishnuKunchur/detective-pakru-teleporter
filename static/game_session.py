"""
class GameSession()

A class that provides attributes and methods for keeping track of events in the game.

Initialize attributes at start of game: UUID, current_level, session_status, num_attempts_level
Methods: validate_level
"""
import sys
import time
import uuid

class GameSession():
    """
    property of: I.C.H.E.P and Vishnu Kunchur
    session attributes and methods to track gameplay in the Teleporter Dormancy Module

    UUID: random uuid.uuid4() session identifier
    current_level: the level the session is currently on
    num_attempts_level: the number of attempts that have been made on the current level
    """

    def __init__(self, mission_staff):
        """
        initialize a game session
        mission_staff: pandas DataFrame object containing all data for mission critical staff
        """
        self.mission_staff = mission_staff
        # staff username-password credentials; dict
        self.mission_staff_credentials = mission_staff[['order', 'username', 'password']]\
                                                .set_index('order').T.to_dict()
        # gameplay attributes
        self.game_session_id = str(uuid.uuid4())
        self.current_level = 1
        self.MAX_LEVEL = 5
        self.num_attempts_level = 0
        self.max_attempts_level = 3
        self.rem_attempts_level = self._calculate_remaining_attempts_level()
        self.status_message = ''
        self.session_verdict = 'play'
        self.lightpanel = self._initialize_lightpanel()
        pass
    
    def reset_session(self):
        """
        reset the GameSession
        """
        self.current_level = 1
        self.num_attempts_level = 0
        self.rem_attempts_level = self._calculate_remaining_attempts_level()
        self.status_message = ''
        self.session_verdict = 'play'
        self.lightpanel = self._initialize_lightpanel()
        pass

    def _initialize_lightpanel(self):
        """
        initialize the lights panel
        """
        lightpanel_colorclass_dict = {}
        for idx in range(1, self.MAX_LEVEL+1):
            lightpanel_colorclass_dict[idx] = 'circle-inactive'
        return lightpanel_colorclass_dict

    def get_current_staff_id(self):
        """
        return the staff ID based on current level
        """
        current_staff_id = self.mission_staff.query("order == {}".format(self.current_level))['id'].values
        if len(current_staff_id) == 0:
            return ''
        else:
            return current_staff_id[0]

    def _calculate_remaining_attempts_level(self):
        return self.max_attempts_level - self.num_attempts_level

    def _fail_username_validation(self):
        """
        username mismatch
        """
        message = 'INCORRECT USERNAME ENTERED. SUSPICIOUS ROGUE ACTIVITY DETECTED. TELEPORTER WILL NOW TERMINATE.'
        print(message)
        self.num_attempts_level += 1
        self.rem_attempts_level = None
        self.session_verdict = 'lost'
        self.status_message = message
        # lightpanel color change: RED
        self.lightpanel[self.current_level] = 'circle-red'
        pass
    
    def _fail_password_validation(self):
        """
        password mismatch
        """
        self.num_attempts_level += 1
        self.rem_attempts_level = self._calculate_remaining_attempts_level()
        message = 'INCORRECT USERNAME/PASSWORD COMBINATION. YOU HAVE {} ATTEMPTS REMAINING.'.format(self.rem_attempts_level)
        #lightbulb color change: YELLOW
        self.lightpanel[self.current_level] = 'circle-yellow'
        if self.rem_attempts_level <= 0:
            message = 'TOO MANY INCORRECT PASSWORD ATTEMPTS WERE MADE. SUSPICIOUS ROGUE ACTIVITY DETECTED. TELEPORTER WILL NOW TERMINATE.'
            self.rem_attempts_level = None
            self.session_verdict = 'lost'
            # lightbulb color change: RED
            self.lightpanel[self.current_level] = 'circle-red'
        print(message)
        self.status_message = message
        pass

    def _pass_username_password_validation(self):
        """
        username and password match
        """
        # no message displayed when level is passed
        message = ''
        print(message)
        # lightbulb color change: GREEN
        self.lightpanel[self.current_level] = 'circle-green'
        self.current_level += 1
        self.num_attempts_level = 0
        self.rem_attempts_level = self._calculate_remaining_attempts_level()
        self.status_message = message
        pass

    def _win_game_check(self):
        """
        check for victory
        """
        if self.current_level > self.MAX_LEVEL:
            self.session_verdict = 'won'
            message = 'VALIDATION SUCCESSFUL. THE TELEPORTER DORMANCY MODULE WILL NOW SWITCH TO ACTIVE STATUS.'
            self.current_level = self.MAX_LEVEL
            self.status_message = message 
        pass

    def _get_status(self):
        return {'level': self.current_level, 
                'num_attempts': self.num_attempts_level, 
                'rem_attempts': self.rem_attempts_level,
                'verdict': self.session_verdict,
                'message': self.status_message}

    def validate_level(self, level, guess):
        """
        level: self.current_level
        guess: dictionary: {'username': guess_username, 'password': guess_password}
        truth: dictionary: {'username': true_username, 'password': true_password}
        """
        truth = self.mission_staff_credentials[level]    
        true_username, true_password = truth.get('username'), truth.get('password')
        assert type(guess) == dict, 'guess must be supplied as a dict!'
        guess_username, guess_password = guess.get('username'), guess.get('password')
        try:
            assert guess_username is not None, 'username must be guessed!'
            assert guess_password is not None, 'password must be guessed!'
            pass
        except AssertionError as e:
            print(e)
            sys.exit(1)

        # ignore newline characters in the guessed password
        guess_password = guess_password.replace('\n', '').replace(' ', '')

        # fail username validation:
        if guess_username != true_username:
            self._fail_username_validation()
            return self._get_status()

        # password validation for level-1:
        if level == 1:
            true_password = float(true_password)
            try:
                guess_password = float(guess_password)
            except:
                self._fail_password_validation()
                return self._get_status()
            if true_password - 1 < guess_password < true_password + 1:
                self._pass_username_password_validation()
                return self._get_status()
            else:
                self._fail_password_validation()
                return self._get_status()
        
        # password mismatch:
        if guess_password != true_password:
            self._fail_password_validation()
            return self._get_status()
            
        # password match
        else:
            self._pass_username_password_validation()
        
        # win game logic
        self._win_game_check()
        
        return self._get_status()
