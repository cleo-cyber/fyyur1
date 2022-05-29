from flask import Blueprint, render_template
from models import *
from app import datetime
import sys
from forms import *
venues = Blueprint("venues", __name__, static_folder="static",
                   template_folder="templates")


@venues.route('/venues')
def venues():
    # TODO: replace with real venues data.

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


@venues.route('/venues/search', methods=['POST'])
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


@venues.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    readVenue = Venue.query.get_or_404(venue_id)
    try:
        # show=Show.query.all()
        shows = Show.query.all()
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


@venues.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(formdata=None)
    return render_template('forms/new_venue.html', form=form)


@venues.route('/venues/create', methods=['POST'])
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
        flash('error has occured')
    finally:
        db.session.close()
        if not error:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:

            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


@venues.route('/venues/<venue_id>', methods=['DELETE'])
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
