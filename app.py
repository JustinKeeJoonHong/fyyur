#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import app, db, Venue, Artist, Show
from datetime import datetime
from sqlalchemy import desc

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app.config.from_object('config')
moment = Moment(app)
db.init_app(app)


    

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
  venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
  return render_template('pages/home.html',venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue_data = Venue.query.all()
  data = {}
  for venue in venue_data:
    normalized_city = venue.city.lower()
    key = (normalized_city, venue.state)
    if key not in data:
       data[key] = {"city" : venue.city, "state": venue.state, "venues": []}
    data[key]["venues"].append({
        "id": venue.id,
        "name": venue.name,
    })

  areasData = list(data.values())
  

  return render_template('pages/venues.html', areas=areasData)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_content=request.form.get('search_term', '')
  find_venues = Venue.query.filter(Venue.name.ilike(f'%{search_content}%') | Venue.city.ilike(f'%{search_content}%') | Venue.genres.ilike(f'%{search_content}%')).all()
  countNum = 0
  data = []
  for venue in find_venues:
     countNum += 1
     data.append({
        "id" : venue.id,
        "name" : venue.name,
        "num_upcoming_shows" : 0
     })

  response={
    "count": countNum,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  
  if not venue:
     return render_template('errors/404.html'), 404
  
  # Get current date and time
  current_time = datetime.now()

    # Get upcoming shows
  upcoming_shows_query = Show.query.join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
  upcoming_shows = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  } for show in upcoming_shows_query]

    # Get past shows
  past_shows_query = Show.query.join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
  past_shows = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    } for show in past_shows_query]
  
  data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','), 
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows": past_shows,
        "past_shows_count": len(past_shows)
        
  }
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
  try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      
  except ValueError as e:
      print(e)
      flash('there is invalid value.')
      db.session.rollback()
  finally:
      db.session.close()  

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect('/')





@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):

  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  action = request.form.get('action', '')
  if action == 'delete':
    try:
      venue = Venue.query.get(venue_id)
      if venue:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue successfully deleted.')
      else:
        flash('Venue not found.')
    except Exception as e:
      db.session.rollback()
      flash(f'An error occurred. {e}')
    finally:
      db.session.close()
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  artist_data = Artist.query.all()
  data = []
  for artist in artist_data:
     data.append({
        "id" : artist.id,
        "name": artist.name
     })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".


  search_content=request.form.get('search_term', '')
  find_artists = Artist.query.filter(Artist.name.ilike(f'%{search_content}%') |  Artist.genres.ilike(f'%{search_content}%')).all()
  countNum = 0
  data = []
  for artist in find_artists:
     countNum += 1
     data.append({
        "id" : artist.id,
        "name" : artist.name,
        "num_upcoming_shows" : 0
     })

  response={
    "count": countNum,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  artist = Artist.query.get(artist_id)
  
  if not artist:
     return render_template('errors/404.html'), 404
  
  current_time = datetime.now()
  upcoming_shows_query = Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
  upcoming_shows = [{
       "venue_id": show.venue.id,
       "venue_name": show.venue.name,
       "venue_image_link": show.venue.image_link,
       "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
   } for show in upcoming_shows_query]
  
  past_shows_query = Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
  past_shows = [{
       "venue_id": show.venue.id,
       "venue_name": show.venue.name,
       "venue_image_link": show.venue.image_link,
       "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
   } for show in past_shows_query]

  data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','), 
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows": past_shows,
        "past_shows_count": len(past_shows)
        
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
      artist = Artist.query.filter_by(id=artist_id).first()
      if artist:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form['genres'] 
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website_link = request.form.get('website_link', '') 
        artist.seeking_venue = 'seeking_venue' in request.form
        artist.seeking_description = request.form.get('seeking_description', '')

        db.session.commit()
      else:
        error = True
        flash('Artist not found!')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    return jsonify({"error": str(e)}), 500
  finally:
    db.session.close()

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
      venue = Venue.query.filter_by(id=venue_id).first()
      if venue:
        venue.name = request.form['name']
        city = request.form['city'].strip()
        venue.city = city[0].upper() + city[1:].lower()
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form['genres'] 
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website_link = request.form.get('website_link', '') 
        venue.seeking_talent = 'seeking_talent' in request.form
        venue.seeking_description = request.form.get('seeking_description', '')

        db.session.commit()
      else:
        error = True
        flash('Venue not found!')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    return jsonify({"error": str(e)}), 500
  finally:
    db.session.close()

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  
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
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        
    except ValueError as e:
        print(e)
        flash('there is invalid value.')
        db.session.rollback()
    finally:
        db.session.close()  

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect('/')

  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = Show.query.all()
  data=[]
  for show in shows:
     is_upcoming = show.start_time> datetime.now()
     data.append({
      "venue_id" : show.venue_id,  
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time)),
      "is_upcoming": is_upcoming
     })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  form = ShowForm(request.form)
  if form.validate():  
        try:
            show = Show()
            form.populate_obj(show)
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except Exception as e:  
            db.session.rollback()
            flash('An error occurred. Show could not be listed. ' + str(e))
        finally:
            db.session.close()
  else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f'Error in {fieldName} - {err}')
        return render_template('forms/new_show.html', form=form)  

  return redirect('/')


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
