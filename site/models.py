from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(100))
    pwdhash = db.Column(db.String(54))
    squad_id = db.Column(db.Integer)
    reset_token = db.Column(db.String(20))

    def __init__ (self, first_name, last_name, email, username, password, squad_id=1):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.username = '@' + username
        self.set_password(password)
        self.squad_id = squad_id

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class League(db.Model):
    __tablename__ = 'leagues'
    league_id = db.Column(db.Integer, primary_key = True)
    league_name = db.Column(db.String(100))
    league_pwd = db.Column(db.String(100))
    owner_id = db.Column(db.Integer)

    def __init__ (self, league_name, league_pwd, owner_id):
        self.league_name = league_name
        self.league_pwd = league_pwd
        self.owner_id = owner_id

class Squad(db.Model):
    __tablename__ = 'squads'
    squad_id = db.Column(db.Integer, primary_key = True)
    squad_name = db.Column(db.String(100))
    squad_pwd = db.Column(db.String(100))
    leader_id = db.Column(db.Integer)

    def __init__ (self, squad_name, squad_pwd, leader_id):
        self.squad_name = squad_name
        self.squad_pwd = squad_pwd
        self.leader_id = leader_id

class LeagueUser(db.Model):
    __tablename__ = 'leagues_users'
    row_id = db.Column(db.Integer, primary_key = True)
    league_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__ (self, league_id, user_id):
        self.league_id = league_id
        self.user_id = user_id

class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key = True)
    team_name = db.Column(db.String(120))
    os_team_name = db.Column(db.String(120))
    conference_id = db.Column(db.Integer)
    division = db.Column(db.String(120))
    primary_color = db.Column(db.String(10))
    secondary_color = db.Column(db.String(10))

    def __init__ (self, team_name, os_team_name, conference_id, division, primary_color, secondary_color):
        self.team_name = team_name
        self.os_team_name = os_team_name
        self.conference_id = conference_id
        self.division = division
        self.primary_color = primary_color
        self.secondary_color = secondary_color

class Pick(db.Model):
    __tablename__ = 'picks'
    pick_id = db.Column(db.Integer, primary_key = True)
    league_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    game_id = db.Column(db.Integer)
    is_special = db.Column(db.Boolean)

    def __init__ (self, league_id, user_id, game_id, is_special):
        self.league_id = league_id
        self.user_id = user_id
        self.game_id = game_id
        self.is_special = is_special
