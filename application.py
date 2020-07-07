################################
# OSGA - application.py        #
# Written by Charlotte Lafage  #
# (GitHub: Miloceane)          #
# For Minor Programmeren       #
# (Universiteit van Amsterdam) #
################################

import os
import sys
import json
import hashlib

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, login_fresh, current_user
from sqlalchemy import and_
from requests import get

from models import *
from helpers import *
from import_characters import CharactersList

#--------------------------------------------------------------------------------------------------
#########################
# GENERAL CONFIGURATION #
#########################

# IMPORTANT: Setting this variable to True allows anyone to access Flask Admin via /admin. Always set back to False before deploying!
g_is_local = False

# TODO: Change global variable names to make them start with g_, as to show that they are global.

# Configure Flask app
app = Flask(__name__)
app.secret_key = "dd9fadd2de6003bf66cbe5ecdb6551015150fd955811ba1e8217d76c21f5f974" #os.environ["SECRET_KEY"]


# Configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure API connexion
# Note: this would probably be better put somewhere safer such as in the database
api_id = '9cba8155f5e9c914ace595df9e6e57efc8bf073b3e69de3aba717a147a634a27'
api_key = 'e2e38b259acb59d88cd855a3af7a9f60c8dab289592f73ee1f1bdba9877dda5d'
headers = { 'Content-Type': 'application/json', 'trakt-api-key': '9cba8155f5e9c914ace595df9e6e57efc8bf073b3e69de3aba717a147a634a27', 'trakt-api-version': '2'}

# Configure mail
# TODO: store credentials in db or somewhere else that's safe
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_USERNAME"] = 'osga.staff@gmail.com'
app.config["MAIL_DEFAULT_SENDER"] = 'osga.staff@gmail.com'
app.config["MAIL_PASSWORD"] = 'dany0000'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEBUG"] = True
mail = Mail(app)

# Configure Flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "/"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#--------------------------------------------------------------------------------------------------
##########################
# DATABASE CONFIGURATION #
##########################

# FLASK ADMIN - ONLY USE IN LOCAL TESTING, DO NOT DEPLOY IF is_local IS True!
# (Allows database access to anyone going to /admin from OSGA's main page)
# Configure database models 
if g_is_local:
	admin = Admin(app, name='OSGA Aministration', template_mode='bootstrap3')
	admin.add_view(ModelView(Users, db.session))
	admin.add_view(ModelView(Universes, db.session))
	admin.add_view(ModelView(Shows, db.session))
	admin.add_view(ModelView(FavouritedShows, db.session))
	admin.add_view(ModelView(BlacklistedShows, db.session))
	admin.add_view(ModelView(FlowerTypes, db.session))
	admin.add_view(ModelView(Characters, db.session))
	admin.add_view(ModelView(CharactersFlowers, db.session))
	admin.add_view(ModelView(CharactersMessages, db.session))
	admin.add_view(ModelView(Suggestions, db.session))

# Configure migrations
Migrate(app, db, render_as_batch=True)



#--------------------------------------------------------------------------------------------------
###############
# MAIN ROUTES #
###############

def main():
	db.create_all()

if __name__ == "__main__":
	with app.app_context():
		main()

@app.route("/")
def index():
	""" Index page """
	list_shows = Shows.query.all()
	return render_template("index.html", title="OSGA: One Site to Grieve them All", shows=list_shows)



#--------------------------------------------------------------------------------------------------
#######################
# DATABASE MAGANEMENT #
#######################

@app.route("/create_db")
def create_db():
	""" Creates tables based on db.model inherited classes in models.py """
	db.create_all()
	return "Database created."


@app.route("/empty_db")
def empty_db():
	""" Deletes all tables and data in database, resets user session """
	db.drop_all()
	current_user.name = None
	current_user.id = None
	return "Database emptied."


@app.route("/import_characters")
def import_to_db():
	""" Reads CSV file and imports characters to database """
	characters = CharactersList("Characters.csv")
	message = characters.import_characters()
	return message


#--------------------------------------------------------------------------------------------------
######################
# CEMETARIES: ROUTES #
######################

@app.route("/search_cemetary", methods=["GET", "POST"])
def search_cemetary():
	""" Searches show among shows with a cemetary in database """

	show_name = request.form.get("cemetary_search")
	show_query = Shows.query.filter_by(name=show_name)

	if show_query.count() > 0:
		return redirect(f"/cemetary/{ show_query.first().id }")

	return render_template("layout_message.html", error="There is no cemetary for this show (yet)!")


@app.route("/cemetary/<int:cemetary_id>", methods=["GET", "POST"])
def cemetary(cemetary_id):
	""" Displays cemetary """

	show_query = Shows.query.filter_by(id=cemetary_id).first()

	if request.form.get("graves_sorting") == "popularity":
		cemetary_query = Characters.query.filter_by(show_id=cemetary_id).order_by(Characters.flower_count.desc())
	
	else:
		cemetary_query = Characters.query.filter_by(show_id=cemetary_id).order_by(Characters.id)


	for character in cemetary_query:
		quick_sort_flowers(character.flowers, 0, len(character.flowers) - 1)

	if current_user is None or current_user.is_authenticated is False:
		is_blocked = False
		is_spoiler = False
	else:
		is_blocked = current_user.blocked
		spoiler_query = BlacklistedShows.query.filter(and_(BlacklistedShows.user_id == current_user.id, BlacklistedShows.show_id == cemetary_id)).first()
		is_spoiler = (spoiler_query != None)

	return render_template("cemetary.html", graves_count=cemetary_query.count(), characters=cemetary_query.all(), show_title=show_query.name, show_id=show_query.id, is_blocked=is_blocked, is_spoiler=is_spoiler)


@app.route("/api", methods=["GET"])
def api():
	""" Page for api tests """
	api_request = get('https://api.trakt.tv/shows/popular', headers=headers).json()
	return 	


@app.route("/character/<int:character_id>", methods=["GET"])
def character(character_id):
	""" Displays character info """

	character = Characters.query.get(character_id)
	show = Shows.query.get(character.show_id)

	return render_template("character.html", character=character, show_name=show.name)


#--------------------------------------------------------------------------------------------------
####################
# CEMETARIES: AJAX #
####################

@app.route("/save_flower/<int:character_id>/<int:flowertype_id>/<int:pos_x>/<int:pos_y>", methods=["GET"])
def save_flower(character_id, flowertype_id, pos_x, pos_y):
	""" Saves the flower with flowertype flowertype_id and position (pos_x, pos_y) in database for character character_id. """

	# Just in case the user tried to artificially insert JS to bypass blocked account and leave flower (idk who would do that, but who knows)
	if current_user.is_authenticated:
		user = Users.query.get(current_user.id)
		if user.blocked:
			return ""

	curr_char = Characters.query.get(character_id)
	curr_char.flower_count = curr_char.flower_count + 1

	db.session.add(CharactersFlowers(flowertype_id=flowertype_id, character_id=character_id, pos_x=pos_x, pos_y=pos_y))	
	db.session.commit()
	return ""


@app.route("/save_message", methods=["POST"])
@login_required
def save_message():
	""" Saves message sent via POST in database. """

	# Just in case the user tried to artificially insert JS to bypass blocked account and leave message
	user = Users.query.get(current_user.id)
	if (user and user.blocked):
		return ""

	message = request.get_json()
	message_content = message.get("message")
	message_user_id = message.get("user_id")
	character_id = message.get("character_id")
	db.session.add(CharactersMessages(user_id=message_user_id, character_id=character_id, content=message_content))
	db.session.commit()
	return message
	
#--------------------------------------------------------------------------------------------------
########################
# REGISTER / LOGIN-OUT #
########################

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
	""" Registers the user based on POST data sent from register.html """

	# User is already registered + logged_in
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Receiving registration form
	if request.form.get("username"):
		username = request.form.get("username")
		password = request.form.get("password")
		password_confirmation = request.form.get("password_confirmation")
		email = request.form.get("email")
		email_confirmation = request.form.get("email_confirmation")
		error = ""

		# NOTE: isalnum() was used here to force usernames to contain only alphanumeric characters in order to protect against SQL injections,
		# but SQLAlchemy already makes them technically impossible, so this is probably not necessary.
		if not username.isalnum():
			error += "Your username can only contain letters or numbers. "
		
		if len(password) < 6:
			error += "Your password must be at least 6 characters long. "	

		if password != password_confirmation:
			error += "Password and confirmation didn't match! "

		# TODO: check email validity. Library? Regex?
		if email != email_confirmation:
			error += "Email and confirmation didn't match! "

		email_exist_query = Users.query.filter_by(email=email).count()
		if email_exist_query > 0:
			error += "This email address is already taken!"

		if error != "":
			return render_template("register.html", error=error)

		# TODO: apparently md5 isn't safe anymore? Check what to use instead.
		password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

		new_user = Users(name=username, password=password_hash, email=email)
		db.session.add(new_user)
		db.session.commit()

		confirmation_message_title = f"Registration on OSGA"
		confirmation_message_html = f"Hello { username },<br><br>Thank you for registering on OSGA!"
		msg = Message(confirmation_message_title, sender="noreply@osga.com", recipients=[email])
		msg.html = confirmation_message_html
		mail.send(msg)

		return render_template("layout_message.html", message="Thank you for registering. Your account has been created! You can now log-in and get access to more features.")
	
	return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
	""" Logs user in and redirects to currently visited page """
	if request.form.get("username") and request.form.get("password"):

		username_input = request.form.get("username")
		password_input = request.form.get("password")
		
		# NOTE: isalnum() was used here to force usernames to contain only alphanumeric characters in order to protect against SQL injections,
		# but SQLAlchemy already makes them technically impossible, so this is probably not necessary.
		if username_input.isalnum():
			password_hash = hashlib.md5(password_input.encode('utf-8')).hexdigest()
			login_request = Users.query.filter(and_(Users.name == username_input, Users.password == password_hash))

			if login_request.count() == 0:
				# TODO: either make a log-in page to redirect the user, or check this in JS, this is tiresome for users.
				flash("Username and password didn't match.")
				return render_template("layout_message.html", error="Your username and password didn't match.")

			
			else:
				user = login_request.first()
				login_user(user, remember = not (request.form.get("remember_me") is None))
				
	return redirect(request.referrer)



@app.route("/logout", methods=["GET", "POST"])
def logout():
	""" Logs user out and redirects to currently visisted page """
	logout_user()
	# current_user.name = None
	# current_user.id = None
	return redirect(request.referrer)



#--------------------------------------------------------------------------------------------------
#############
# USER INFO #
#############

@app.route("/user_panel", methods=["GET"])
@login_required
def user_panel_default():
	""" Returns default user panel tab """	
	return user_panel("")


@app.route("/user_panel/<string:page_type>", methods=["GET", "POST"])
@login_required
def user_panel(page_type):
	""" Returns specified user panel page if it exists, otherwise default. """

	if current_user.id is None:
		return redirect("/")

	user = Users.query.get(current_user.id)
	error_message = ""
	success_message = ""

	#---- Display User settings tab ----#
	if page_type == "user_settings": 
		if request.form.get("password"):
			if request.form.get("password") != request.form.get("password_confirmation"):
				error_message += "Password and password confirmation didn't match! "
			elif len(request.form.get("password")) < 6:
				error_message += "Password should be at least 6 characters long. "
			elif login_fresh() is False:
				error_message += "You are using an old session, please log out and log in again to change your password."
			else:
				success_message += "Your password has been changed! "
				user.password = hashlib.md5(request.form.get("password").encode('utf-8')).hexdigest()
				db.session.commit()
		
		if request.form.get("email"):
			if request.form.get("email") != request.form.get("email_confirmation"):
				error_message += "E-mail address and confirmation didn't match! "
			elif login_fresh() is False:
				error_message += "You are using an old session, please log out and log in again to change your e-mail address."
			else:
				success_message += "Your e-mail address has been changed! "
				user.email = request.form.get("email")
				db.session.commit()

		if request.form.get("update_pref"):
			user.display_fav = not (request.form.get("display_favourite") is None)
			user.display_activity = not (request.form.get("display_activity") is None)
			db.session.commit()

		return render_template("user_panel.html", selected_user_settings="active", user_info=user, error=error_message, success=success_message, fresh_session=login_fresh())


	#---- Display Suggestions tab ----#
	elif page_type == "suggestions":

		confirmation = ""
		
		# TODO: protect against HTML injections? (Or does SQLAlchemy also escape HTML?)
		if request.form.get("suggest_show") or request.form.get("other_suggestion"):
			show = request.form.get("suggest_show")
			other_suggestion = request.form.get("other_suggestion")
			db.session.add(Suggestions(user_id=current_user.id, show=show, content=other_suggestion))
			db.session.commit()

			confirmation = "Your suggestion has been registered and the cemetaries' maintenance will review it, thanks!"

		return render_template("user_panel.html", selected_suggestions="active", error=confirmation)


	#---- Display Shows settings tab ----#
	else:
		shows = Shows.query.all()

		if request.form.get("add_favourite"):
			new_fav_id = int(request.form.get("add_favourite"))
			db.session.add(FavouritedShows(user_id=user.id, show_id=new_fav_id))
			db.session.commit()

		if request.form.get("add_blacklist"):
			new_blacklist_id = int(request.form.get("add_blacklist"))
			db.session.add(BlacklistedShows(user_id=user.id, show_id=new_blacklist_id))
			db.session.commit()

		if request.form.get("remove_favourited"):
			old_fav_id = int(request.form.get("remove_favourited"))
			old_fav = FavouritedShows.query.filter(and_(FavouritedShows.user_id == user.id, FavouritedShows.show_id == old_fav_id))
			db.session.delete(old_fav.first())
			db.session.commit()

		if request.form.get("remove_blacklisted"):
			old_blacklist_id = int(request.form.get("remove_blacklisted"))
			old_blacklist = BlacklistedShows.query.filter(and_(BlacklistedShows.user_id == user.id, BlacklistedShows.show_id == old_blacklist_id))
			db.session.delete(old_blacklist.first())
			db.session.commit()

		user_favourite = Shows.query.join(FavouritedShows, FavouritedShows.show_id == Shows.id, isouter=True).filter(FavouritedShows.user_id == user.id)
		user_blacklist = Shows.query.join(BlacklistedShows, BlacklistedShows.show_id == Shows.id, isouter=True).filter(BlacklistedShows.user_id == user.id)

		return render_template("user_panel.html", selected_shows_settings="active", shows=shows, favourite_shows=user_favourite, favourite_shows_count=user_favourite.count(), blacklisted_shows=user_blacklist, blacklisted_shows_count=user_blacklist.count())


@app.route("/user_profile/<int:user_profile_id>", methods=["GET"])
def user_profile(user_profile_id):	
	""" Displays user profile information """
	
	user_profile = Users.query.get(user_profile_id)
	user_favourite = []

	if not user_profile:
		return redirect(request.referrer)

	if user_profile.display_fav:
		user_favourite = Shows.query.join(FavouritedShows, FavouritedShows.show_id == Shows.id, isouter=True).filter(FavouritedShows.user_id == user_profile.id)
	
	activity_total = []	
	# activity_flowers = CharactersFlowers.query.filter_by(user_id=user_profile)
	# activity_messages = CharactersMessages.query.filter_by(user_id=user_profile)
	# activity_total = activity_flowers + activity_messages
	# activity_total.sort(key=lambda x: x.date, reverse=True)

	# for act in activity_total:
	# 	act['type'] = "flower" if isinstance(act, CharactersFlowers) else "message"

	return render_template("user_profile.html", user_profile_name=user_profile.name, user_profile_favourite_shows=user_favourite, activity=activity_total[:50])



#--------------------------------------------------------------------------------------------------
##################
# ADMINISTRATION #
##################

@app.route("/admin_panel", methods=["GET"])
@login_required
def admin_panel_default():
	""" Returns default admin panel tab """
	return admin_panel("")


@app.route("/admin_panel/<string:page_type>", methods=["GET", "POST"])
@login_required
def admin_panel(page_type):
	""" Returns specified admin panel tab if it exists, otherwise default. """

	if not current_user.id:
		return redirect("/")

	user_request = Users.query.filter_by(id=current_user.id).first()
	if user_request.admin_level < 1:
		return redirect("/")		

	message = ""

	#---- Declare character death ----#
	if page_type == "declare_death":
		# TODO: Add a way to make import of dead characters in database faster because really for newly added series this takes forever
		# and I don't know if I can trust other admins enough to let them use the .csv import.

		if request.form.get("character"): # Receive death declaration
			# TODO: Add some protection against injections here in case an admin suddenly decides to hack the website (been there)
			# TODO: Maybe switch to OMDB API? Track seems to have issues matching IMDB ids...
			show_api_id = "0" # Old code for reference: if request.form.get("declare_death_show_search")
			character = request.form.get("character")
			season = request.form.get("declare_death_season")
			episode = request.form.get("declare_death_episode")
			show_title = request.form.get("declare_death_show_search")
			
			show_request = Shows.query.filter_by(name=show_title)
			if show_request.count() == 0: # Show doesn't exist in database yet
				db.session.add(Shows(name=show_title, api_id=show_api_id))
				db.session.commit()
				show_request = Shows.query.filter_by(name=show_title)

			new_character = Characters(name=character, show_id=show_request.first().id, admin_id=current_user.id, death_season=season, death_episode=episode)
			db.session.add(new_character)
			db.session.commit()

			message=f"{ character } has been declared dead on season { season } episode { episode }. Their grave has been added to { show_title }'s cemetary."	

		headers_index_search = headers
		headers_index_search['X-Pagination-Limit'] = '30'
		headers_index_search['X-Pagination-Page'] = '3'
		api_request = get('https://api.trakt.tv/shows/popular', headers=headers_index_search).json()

		return render_template("admin_panel.html", 
			selected_declare_death="active", 
			title="OSGA: One Site to Grieve them All", 
			shows=api_request, 
			message=message)


	#---- Moderate Suggestions ----#
	if page_type == "manage_suggestions":
		# TODO: add pagination
		important_suggestions = Suggestions.query.filter_by(is_important=True).all()
		read_suggestions = Suggestions.query.filter(and_(Suggestions.is_read == True, Suggestions.is_important == False)).all()
		other_suggestions = Suggestions.query.filter(and_(Suggestions.is_important == False, Suggestions.is_read == False)).all()

		# We want suggestions by order of "importance": first those marked as important, at the end those marked as read, in the middle the rest.
		suggestions_list = important_suggestions + other_suggestions + read_suggestions
		suggestions_count = len(suggestions_list)

		return render_template("admin_panel.html", 
			selected_manage_suggestions="active", 
			suggestions=suggestions_list,
			suggestions_count=suggestions_count)


	#---- Moderate comments ----#
	unvalidated_comments = []
	messages_to_validate = CharactersMessages.query.filter_by(admin_id=0)

	if messages_to_validate.count() > 0:
		for message in messages_to_validate:
			new_comment = {}
			message_character = Characters.query.get(message.character_id)
			new_comment['message'] = message
			new_comment['username'] = Users.query.get(message.user_id).name
			new_comment['character_name'] = message_character.name
			new_comment['character_show'] = Shows.query.get(message_character.show_id).name
			unvalidated_comments.append(new_comment)

	return render_template("admin_panel.html", 
		selected_moderate_comments="active", 
		unvalidated_comments=unvalidated_comments)




@app.route("/moderate_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def moderate_comment(comment_id):
	""" Manages comment with id comment_id based on action received via POST data """
	if not current_user.id:
		return redirect("/")

	user_request = Users.query.filter_by(id=current_user.id).first()
	if user_request.admin_level < 1:
		return redirect("/")		

	comment = CharactersMessages.query.get(comment_id)

	if request.form.get("validate"):
		comment.admin_id = current_user.id			
		db.session.commit()

	if request.form.get("refuse"):
		comment.admin_id = -1		
		db.session.commit()

	if request.form.get("block"):
		comment.admin_id = -1
		comment_user = Users.query.get(comment.user_id)
		comment_user.blocked = True			
		db.session.commit()

	return admin_panel("")



@app.route("/manage_suggestions/<int:suggestion_id>", methods=["GET", "POST"])
@login_required
def manage_suggestion(suggestion_id):
	""" Manages suggestion with id suggestion_id based on action received via POST data. """

	if not current_user.id:
		return redirect("/")

	user_request = Users.query.filter_by(id=current_user.id).first()
	if user_request.admin_level < 1:
		return redirect("/")		

	suggestion = Suggestions.query.get(suggestion_id)

	if request.form.get("important"):
		suggestion.is_important = not suggestion.is_important		
		db.session.commit()

	if request.form.get("read"):
		suggestion.is_read = not suggestion.is_read
		db.session.commit()

	if request.form.get("delete"):
		db.session.delete(suggestion)
		db.session.commit()

	if request.form.get("block"):
		suggestion_user = Users.query.get(suggestion.user_id)
		suggestion_user.blocked = True
		db.session.delete(suggestion)
		db.session.commit()

	return admin_panel("manage_suggestions")