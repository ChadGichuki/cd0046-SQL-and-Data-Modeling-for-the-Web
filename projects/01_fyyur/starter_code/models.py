from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import CheckConstraint
from flask_migrate import Migrate
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
db = SQLAlchemy(app)
app.config.from_object('config')
migrate = Migrate(app, db)

class Venue(db.Model):
    """Table stores all the venues"""
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True, default='None')
    facebook_link = db.Column(db.String(120), nullable=True, default='None')
    website_link = db.Column(db.String(120), nullable=True, default='None')
    talent_looking = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(), nullable=True)
    upcoming_shows = db.relationship('Show', backref='venue', lazy=True)
    past_shows = db.relationship('PastShow', backref='venue', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
      return f'<Venue {self.id}, {self.name}>'

class Artist(db.Model):
    """Table stores all the artists"""
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True, default='None')
    facebook_link = db.Column(db.String(120), nullable=True, default='None')
    website_link = db.Column(db.String(120), nullable=True, default='None')
    venue_looking = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(), nullable=True)
    upcoming_shows = db.relationship('Show', backref='artist', lazy=True)
    past_shows = db.relationship('PastShow', backref='artist', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Venue {self.id}, {self.name}>'

class Show(db.Model):
    """
    Table stores all the shows.

    A show can have only one artist and only one show. 
    However, an artist and a venue can have many shows. 
    (One to many relationships with both)
    """
    __tablename__= 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
      return f'<Show {self.id}, {self.start_time}'

class PastShow(db.Model):
    """Table stores all the past shows"""
    __tablename__= 'past_shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, CheckConstraint('datetime.today > start_time'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
      return f'<Past Show {self.id}, {self.start_time}'


