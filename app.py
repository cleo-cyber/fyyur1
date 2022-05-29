#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
import logging
import sys
from email.policy import default
from itertools import count
from logging import FileHandler, Formatter
import babel
import dateutil.parser
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, Form
from sqlalchemy import ForeignKey, desc
from wtforms import StringField, validators
from forms import *
from models import Artist, Show, Venue, db
# from venues import venues

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# app.register_blueprint(venues) blue print was generating errors
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    # venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
    # artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    areas = Venue.query.group_by(Venue.city, Venue.state, Venue.id, Venue.name).distinct(
        Venue.city, Venue.state, Venue.id)

    data = []
    upcoming_shows = []
    for area in areas:

        upcoming_shows_query = db.session.query(Show).join(Venue).filter(
            Show.artist_id == Artist.id).filter(Show.start_time > datetime.now()).all()

        upcoming_shows.append(upcoming_shows_query)

        venues_show = {
            'id': area.id,
            'name': area.name,
            'num_of_upcoming_shows': len(upcoming_shows)
        }
        location = {
            'city': area.city,
            'state': area.state,
            'venues': [venues_show]

        }
        data.append(location)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_query = Venue.query.filter(
        Venue.name.ilike('%'+search_term+'%')).all()
    count = len(search_query)
    data = []

    for serch in search_query:
        show_details = {
            "id": serch.id,
            "name": serch.name,
            "num_of_upcoming_shows": len(str(Show.query.filter(Venue.id == serch.id).filter(Show.start_time > datetime.now())))
        }

        data.append(show_details)
    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    readVenue = Venue.query.get_or_404(venue_id)
    try:

        past_shows = []
        upcoming_shows = []
        past_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
        for show in past_shows_query:
            past = {
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': str(show.start_time)
            }
            past_shows.append(past)
        for show in upcoming_shows_query:
            upcoming = {
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': str(show.start_time)
            }
            upcoming_shows.append(upcoming)

        data = {
            'id': readVenue.id,
            'name': readVenue.name,
            'genres': readVenue.genres,
            'address': readVenue.address,
            'city': readVenue.city,
            'state': readVenue.state,
            'phone': readVenue.phone,
            'website': readVenue.website_link,
            'facebook_link': readVenue.facebook_link,
            'seeking_talent': readVenue.seeking_talent,
            'seeking_description': readVenue.seeking_description,
            'image_link': readVenue.image_link.strip('"'),
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)


        }
    except:
        print(sys.exc_info())
        flash('error has occured')

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(formdata=None)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm()
    try:

        if form.validate_on_submit():

            newVenue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data)
            db.session.add(newVenue)
            db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:

            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        Venue.query.filter_by(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.group_by(
        Artist.id, Artist.name).distinct(Artist.name, Artist.id)

    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_query = Artist.query.filter(
        Artist.name.ilike('%'+search_term+'%')).all()
    count = len(search_query)
    data = []
    for search in search_query:
        artist_data = {
            'id': search.id,
            'name': search.name,
            'num_upcoming_shows': len(str(Show.query.filter(Artist.id == search.id).filter(Show.start_time > datetime.now())))
        }
        data.append(artist_data)
    response = {
        'count': count,
        'data': data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    artist = Artist.query.filter(Artist.id == artist_id).first()
    upcoming_shows = []
    past_Shows = []
    past_show_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now())
    upcoming_Show_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now())
    try:

        for show in past_show_query:
            past = {
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image': show.venue.image_link,
                'start_time': str(show.start_time)
            }
            past_Shows.append(past)
        for show in upcoming_Show_query:
            upcoming = {
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image': show.venue.image_link,
                'start_time': str(show.start_time)
            }
            upcoming_shows.append(upcoming)

        data = {
            'id': artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'webiste': artist.website_link,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link.strip('"'),
            'past_shows': past_Shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_Shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
    except:
        flash('error occured')

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(formdata=None)
    artist = Artist.query.filter(Artist.id == artist_id).first()
    if artist:

        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website_link
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    update_artist = Artist.query.get_or_404(artist_id)
    try:
        if form.validate_on_submit():
            update_artist.name = form.name.data
            update_artist.city = form.city.data
            update_artist.state = form.state.data
            update_artist.phone = form.phone.data
            update_artist.image_link = form.image_link.data
            update_artist.facebook_link = form.facebook_link.data
            update_artist.website_link = form.website_link.data
            update_artist.seeking_venue = form.seeking_venue.data
            update_artist.seeking_description = form.seeking_description.data
            update_artist.genres = form.genres.data
            db.session.add(update_artist)
            db.session.commit()
            flash('artists has been updated successfuly')
    except:
        db.session.rollback()
        flash('There was an error on the update!')
        print(sys.exc_info())
    finally:

        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(formdata=None)
    venue = Venue.query.filter(Venue.id == venue_id).first()

    if venue:

        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website_link
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link.strip('"')

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_update = Venue.query.get_or_404(venue_id)

    form = VenueForm()
    try:
        if form.validate_on_submit():

            venue_update.name = form.name.data,
            venue_update.city = form.city.data,
            venue_update.state = form.state.data,
            venue_update.phone = form.phone.data,
            venue_update.website_link = form.website_link.data,
            venue_update.facebook_link = form.facebook_link.data,
            venue_update.seeking_description = form.seeking_description.data,
            venue_update.seeking_Talent = form.seeking_talent.data,
            venue_update.address = form.address.data,
            venue_update.genres = form.genres.data,
            venue_update.image_link = form.image_link.data.strip('"')

            db.session.commit()
        flash('venue updated successfully')

    except:
        db.session.rollback()
        flash('there was an error on the updates')

    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm(formdata=None)
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm()
    try:
        if form.validate_on_submit():
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                genres=form.genres.data

            )
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    shows = Show.query.all()
    data = []
    for show in shows:
        real_venues = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link.strip('"'),
            'start_time': str(show.start_time)

        }
        data.append(real_venues)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm(formdata=None)
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()
    try:
        if form.validate_on_submit():
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(405)
def invalid_method(error):
    return render_template('errors/405.html')


@app.errorhandler(409)
def duplicate_resource(error):
    return render_template('errors/409.html')


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
