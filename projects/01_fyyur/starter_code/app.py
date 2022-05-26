#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from audioop import add
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import CheckConstraint, desc
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    """Table stores all the venues"""
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=True, default='None')
    facebook_link = db.Column(db.String(120), nullable=True, default='None')
    website_link = db.Column(db.String(120), nullable=True, default='None')
    talent_looking = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(), nullable=True)
    upcoming_shows = db.relationship('Show', backref='venue', lazy=True)
    past_shows = db.relationship('PastShow', backref='venue', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
   
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
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=True, default='None')
    facebook_link = db.Column(db.String(120), nullable=True, default='None')
    website_link = db.Column(db.String(120), nullable=True, default='None')
    venue_looking = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(), nullable=True)
    upcoming_shows = db.relationship('Show', backref='artist', lazy=True)
    past_shows = db.relationship('PastShow', backref='artist', lazy=True)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    

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
    start_time = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
      return f'<Show {self.id}, {self.start_time}'

class PastShow(db.Model):
    """Table stores all the past shows"""
    __tablename__= 'past_shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
      return f'<Past Show {self.id}, {self.start_time}'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # Retrieve the 10 latest venues and artists to display on home page
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()

  return render_template('pages/home.html', recent_artists=artists, recent_venues=venues)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  #data = [{
  #  'city': db.session.query(Venue.city).distinct().all(), 
  # 'state': db.session.query(Venue.state).distinct().all(),
  #  'venues': db.session.query(Venue.name).all()}]
  data = db.session.query(Venue.city, Venue.state, Venue.name.label('venues')).all()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search on venues with partial string search. Is case-insensitive.
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  response = Venue.query.filter(Venue.name.like(search)).all()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  data = Venue.query.get_or_404(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  genres = form.genres.data
  facebook = form.facebook_link.data
  image = form.image_link.data
  website = form.website_link.data
  talent = form.seeking_talent.data
  desc = form.seeking_description.data

  venue = Venue(name=name, city=city, state=state, address=address, 
  phone=phone, genres=genres, facebook_link=facebook, image_link=image,website_link=website, talent_looking=talent, description=desc)

  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed')
    # on unsuccessful db insert, flash an error instead.

  finally:
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>/delete', methods=['GET','DELETE'])
def delete_venue(venue_id):
    """Deletes records of a venue"""
    venue_to_delete = Venue.query.get_or_404(venue_id)

    try:
      db.session.delete(venue_to_delete)
      db.session.commit()
      flash("Venue deleted successfully!")
    except:
      db.session.rollback()
      db.session.commit()
      flash('An error occurred. Could not delete task')
    finally:
      return redirect(url_for('index'))
     
      

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data = Artist.query.order_by(Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search on artists with partial string search. Is case-insensitive.

  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  response = Artist.query.filter(Artist.name.like(search.lower() or search.upper() or search.title()))
  response = {'data': response.order_by(Artist.name).all(), 'count': response.count()}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = Artist.query.get_or_404(artist_id)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_to_edit = Artist.query.get_or_404(artist_id)
  form.name.data = artist_to_edit.name
  form.city.data = artist_to_edit.city
  form.state.data = artist_to_edit.state
  form.phone.data = artist_to_edit.phone
  form.genres.data = artist_to_edit.genres
  form.facebook_link.data = artist_to_edit.facebook_link
  form.image_link.data = artist_to_edit.image_link
  form.website_link.data = artist_to_edit.website_link
  form.seeking_venue.data = artist_to_edit.venue_looking
  form.seeking_description.data = artist_to_edit.description
  
  return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist_to_edit = Artist.query.get_or_404(artist_id)
  artist_to_edit.name = form.name.data
  artist_to_edit.city = form.city.data
  artist_to_edit.state = form.state.data
  artist_to_edit.phone = form.phone.data
  artist_to_edit.genres = form.genres.data
  artist_to_edit.facebook_link = form.genres.data
  artist_to_edit.image_link = form.image_link.data
  artist_to_edit.website_link = form.website_link.data
  artist_to_edit.venue_looking = form.seeking_venue.data
  artist_to_edit.description = form.seeking_description.data

  try:
    db.session.commit()
    flash("Artist updated successfully!")
  except:
    db.session.rollback()
    flash("An error occurred. Could not update artist")
  finally:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_to_edit = Venue.query.get_or_404(venue_id)
  form.name.data = venue_to_edit.name
  form.city.data = venue_to_edit.city
  form.state.data = venue_to_edit.state
  form.address.data = venue_to_edit.address
  form.phone.data = venue_to_edit.phone
  form.genres.data = venue_to_edit.genres
  form.facebook_link.data = venue_to_edit.facebook_link
  form.image_link.data = venue_to_edit.image_link
  form.website_link.data = venue_to_edit.website_link
  form.seeking_talent.data = venue_to_edit.talent_looking
  form.seeking_description.data = venue_to_edit.description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  venue_to_edit = Venue.query.get_or_404(venue_id)
  venue_to_edit.name = form.name.data
  venue_to_edit.city = form.city.data
  venue_to_edit.state = form.state.data
  venue_to_edit.address = form.address.data
  venue_to_edit.phone = form.phone.data
  venue_to_edit.genres = form.genres.data
  venue_to_edit.facebook_link = form.facebook_link.data
  venue_to_edit.image_link = form.image_link.data
  venue_to_edit.website_link = form.website_link.data
  venue_to_edit.talent_looking = form.seeking_talent.data
  venue_to_edit.description = form.seeking_description.data

  try:
    db.session.commit()
    flash("Venue updated successfully!")
  except:
    flash('An error occurred. Could not update venue.')
    db.session.rollback()
  finally:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  facebook = form.facebook_link.data
  image = form.image_link.data
  website = form.website_link.data
  venue = form.seeking_venue.data
  desc = form.seeking_description.data

  artist = Artist(name=name, city=city, state=state, 
  phone=phone, genres=genres, facebook_link=facebook, image_link=image,website_link=website, venue_looking=venue, description=desc)

  try:
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist' + request.form['name'] + 'could not be listed')
    # on unsuccessful db insert, flash an error instead.

  finally:
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  
  data = db.session.query(Show, Artist, Venue)\
    .join(Artist, Artist.id == Show.artist_id)\
      .join(Venue, Venue.id == Show.venue_id).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  time = form.start_time.data

  # Add the shows count to the venue and artist tables respectively
  
  Artist.upcoming_shows_count += 1
  Venue.upcoming_shows_count += 1
  show = Show(artist_id=artist_id, venue_id=venue_id, start_time=time)

  #else:
    #Artist.past_shows_count += 1
    #Venue.past_shows_count += 1
    #show = PastShow(artist_id=artist_id, venue_id=venue_id, start_time=time)

  # Commit the changes to the db
  try:
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    # on unsuccessful db insert, flash an error instead.
  finally:
    return render_template('pages/home.html')

@app.route('/shows/search', methods=['POST'])
def search_shows():
  """Handles search for shows based on artist name"""
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  response = Show.query.filter_by(Show.artist_id == Artist.id.filter(Artist.name.like(search))).all()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
