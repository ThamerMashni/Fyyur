#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify 
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate =Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
artists_genres = db.Table('artists_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)
venues_genres = db.Table('venues_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', secondary=venues_genres,
      backref=db.backref('venues', lazy=True))
    website = db.Column(db.String(500))
    seeking_talent =db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show',cascade='all,delete', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary=artists_genres,
      backref=db.backref('artists', lazy=True))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue =db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show',cascade='all,delete', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
    artist_name = db.Column(db.String)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
    venue_name = db.Column(db.String)
    artist_image_link =db.Column(db.String(500))
    venue_image_link =db.Column(db.String(500))
    start_time = db.Column(db.DateTime())
   
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value,str):
    date = dateutil.parser.parse(value)   
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"

  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues_query= Venue.query.all()

  areas = Venue.query.distinct(Venue.city).all()

  data=[]
  now = datetime.now()
  # venue_shows = venues_query[0].shows   #[1].start_time
  # num_upcoming_shows = len(list(filter(lambda show: (show.start_time>now),venue_shows)))

  # print(num_upcoming_shows)
  # print(now)
  # print(now>venue_time)

  for area in areas:
    venues_in_area = []
    for venue in venues_query :
      if area.city in venue.city:
        temp_venue = {
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(list(filter(lambda show: (show.start_time>now),venue.shows))),                                          ### todo later
        }
        venues_in_area.append(temp_venue)

    temp = {
      "city":area.city,
      "state":area.state,
      "venues":venues_in_area
    }
    data.append(temp)
 
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  # print(search_term.lower())
  query = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()
  # print(query)
  
  now = datetime.now()
  data = []
  for d in query:
    temp = {
      "id":d.id,
      "name":d.name,
      "num_upcoming_shows": len(list(filter(lambda show: (show.start_time>now),d.shows))),                                                        ### todo later
    }
    data.append(temp)

  response={
    "count": len(data),
    "data":data
  }
  return render_template('pages/search_venues.html', results=response,search_term= search_term )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  now = datetime.now()
  venue = Venue.query.get(venue_id)
  past_shows = (list(filter(lambda show: (show.start_time<now),venue.shows)))
  upcoming_shows = (list(filter(lambda show: (show.start_time>now),venue.shows)))
  print(past_shows)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website":venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  valid_genres = Genre.query.all()
  choices = []
  for genre in valid_genres:
    choices.append((genre.name, genre.name)) 

  form = VenueForm()
  form.genres.choices = choices
  # var = validGenres().initiate(valid_genres)
  # print(var)

  return render_template('forms/new_venue.html', form=form )

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  err = ''
  try:
      form = VenueForm(request.form)
      
      if form.validate_on_submit():
        new_venue = Venue(name=form.name.data,city=form.city.data,state=form.state.data,address=form.address.data,phone=form.phone.data,facebook_link=form.facebook_link.data)
        genres_names =form.genres.data
        genres=[]
       
        for gname in genres_names:
          genres.append(Genre.query.filter_by(name=gname).first())

        new_venue.genres = genres

        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      else:
          for fieldName, errorMessages in form.errors.items():
            for error in errorMessages:
              err+= ' error occurred validating ' +fieldName + ': '+ error
              print(err)
          flash('An error occurred. Artist could not be listed. error summary\n: '+ err)
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue =Venue.query.filter_by(id=venue_id).first()
    venue.genres =[]
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[] 
  for artist in artists:
    temp = {
      "id": artist.id,
      "name": artist.name
    }
    data.append(temp)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  query = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  now = datetime.now()

  data = []
  for d in query:
    temp = {
      "id":d.id,
      "name":d.name,
      "num_upcoming_shows": len(list(filter(lambda show: (show.start_time>now),d.shows))),                                                        ### todo later
    }
    data.append(temp)

  response={
    "count": len(data),
    "data":data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  now = datetime.now()
  past_shows = (list(filter(lambda show: (show.start_time<now),artist.shows)))
  upcoming_shows = (list(filter(lambda show: (show.start_time>now),artist.shows)))
  print(past_shows)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  valid_genres = Genre.query.all()
  choices = [] 
  for genre in valid_genres:
    choices.append((genre.name, genre.name)) 

  form = ArtistForm()
  form.genres.choices = choices

  artist=Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  err=''
  try:
      form = ArtistForm(request.form)
      artist = Artist.query.get(artist_id)

      if form.validate_on_submit():
        artist.name = request.form['name'] 
        artist.city = request.form['city'] 
        artist.state = request.form['state'] 
        artist.phone = request.form['phone'] 
        artist.facebook_link = request.form['facebook_link'] 
        
        genres_names =form.genres.data
        genres=[]
       
        for gname in genres_names:
          genres.append(Genre.query.filter_by(name=gname).first())

        artist.genres = genres

        db.session.commit()
        # on successful db insert, flash success
        flash('Artist with id:' + str(artist.id)  + ' was successfully updated!')
      else:
          for fieldName, errorMessages in form.errors.items():
            for error in errorMessages:
              err+= ' error occurred validating ' +fieldName + ': '+ error
              print(err)
          flash('An error occurred. Artist could not be updated. error summary\n: '+ err)

  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist with id: ' + str(artist.id) + ' could not be updated.')
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  valid_genres = Genre.query.all()
  choices = []
  for genre in valid_genres:
    choices.append((genre.name, genre.name)) 


  form = VenueForm()
  form.genres.choices = choices

  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  print(form.phone.data)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  err=''
  try:
      form = VenueForm(request.form)
      if form.validate_on_submit():
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        
        genres_names =form.genres.data
        genres=[]
       
        for gname in genres_names:
          genres.append(Genre.query.filter_by(name=gname).first())

        venue.genres = genres

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue with id:' + str(venue.id)  + ' was successfully updated!')
      else:
        for fieldName, errorMessages in form.errors.items():
            for error in errorMessages:
              err+= ' error occurred validating ' +fieldName + ': '+ error
              print(err)
        flash('An error occurred. Artist could not be listed. error summary\n: '+ err)
        

  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue with id: ' + str(venue.id) + ' could not be updated.')
  finally:
      db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  valid_genres = Genre.query.all()
  choices = [] 
  for genre in valid_genres:
    choices.append((genre.name, genre.name))

  # vg = genValidGenres(choices)
  # print(vg.valid_genres)
  form = ArtistForm()
  form.set_genres(choices)
  # form.define_genres(choices) 
  # form.genres.choices = choices

  return render_template('forms/new_artist.html', form=form)  

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  err=''
  try:
      form = ArtistForm(request.form)
      if form.validate_on_submit():
        new_artist = Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],phone=request.form['phone'],facebook_link=request.form['facebook_link'])
        genres_names =form.genres.data
        genres=[]
       
        for gname in genres_names:
          genres.append(Genre.query.filter_by(name=gname).first())

        new_artist.genres = genres

        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      else:
        for fieldName, errorMessages in form.errors.items():
          for error in errorMessages:
            err+= ' error occurred validating ' +fieldName + ': '+ error
            print(err)
        flash('An error occurred. Artist could not be listed. error summary\n: '+ err)

  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. error: '+ err)
  finally:
      db.session.close()

  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  
 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = [] 
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    temp = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    data.append(temp)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist = Artist.query.get(request.form['artist_id'])
    venue = Venue.query.get(request.form['venue_id'])

    show = Show(start_time= request.form['start_time'])
    show.artist = artist
    show.venue = venue
    show.artist_name = artist.name
    show.venue_name = venue.name
    show.artist_image_link = artist.image_link
    show.venue_image_link = venue.image_link

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
