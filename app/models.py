from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login
from hashlib import md5

teammates = db.Table('teammates',
    db.Column('team_member_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('teammate_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    character = db.relationship('Character', back_populates='player')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship(
        'User', secondary=teammates,
        primaryjoin=(teammates.c.team_member_id == id),
        secondaryjoin=(teammates.c.teammate_id == id),
        backref=db.backref('teammates', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def my_character(self):
        own = Character.query.filter_by(user_id=self.id).first_or_404()
        return own
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def join_team(self, user):
        if not self.in_team_with(user):
            self.team.append(user)

    def leave_team(self, user):
        if self.in_team_with(user):
            self.team.remove(user)
    
    def in_team_with(self, user):
        return self.team.filter(teammates.c.teammate_id == user.id).count() > 0

    def team_characters(self):
        team_members = Character.query.join(
            teammates, (teammates.c.teammate_id == Character.user_id)).filter(
                teammates.c.team_member_id == self.id)
        my_char = Character.query.filter_by(user_id=self.id)
        return team_members.union(my_char).order_by(Character.name.desc())

inv_weapons = db.Table('inv_weapons',
    db.Column('w_owner_id', db.Integer, db.ForeignKey('character.id')),
    db.Column('w_owned_id', db.Integer, db.ForeignKey('weapon.id'))
)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), index=True, unique=True)
    level = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    age = db.Column(db.Integer)
    origin = db.Column(db.String(140))
    current_residence = db.Column(db.String(140))
    born_race = db.Column(db.String(140))
    current_race = db.Column(db.String(140))
    affiliations = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player = db.relationship('User', back_populates='character')
    weapons = db.relationship("Weapon", secondary=inv_weapons, back_populates="wielders")

    def __repr__(self):
        return f'<Character {self.name}>'

class Weapon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    damage = db.Column(db.String(64))
    range = db.Column(db.Integer)
    max_range = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    w_type = db.Column(db.String(64))
    a_type = db.Column(db.String(64))
    properties = db.Column(db.String(128))
    wielders = db.relationship("Character", secondary=inv_weapons, back_populates="weapons")

    def __repr__(self):
        return f'<Weapon {self.name}>'

class Affiliations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)    

    def __repr__(self):
        return f'<Affiliations {self.name}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(140))
    body = db.Column(db.String(900))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Article {self.headline}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))