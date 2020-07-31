################################
# OSGA - application.py        #
# Written by Charlotte Lafage  #
# (GitHub: Miloceane)          #
# For Minor Programmeren       #
# (Universiteit van Amsterdam) #
################################

# import logging

import os
import sys
import json
import base64, scrypt
import random, string
import hashlib
from datetime import datetime, timedelta

from flask import Flask, render_template, request, session, redirect, url_for, flash, escape
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, login_fresh, current_user
from flask_session_captcha import FlaskSessionCaptcha
from flaskext.csrf import csrf, csrf_exempt
from sqlalchemy import and_
from requests import get

from models import *
from helpers import *
from import_characters import CharactersList
from import_shows import ShowsList

#--------------------------------------------------------------------------------------------------
#########################
# GENERAL CONFIGURATION #
#########################

# IMPORTANT: Setting this variable to True allows anyone to access Flask Admin via /admin. Always set back to False before deploying!
g_is_local = False

# logging.basicConfig(filename='./osga.log',level=logging.DEBUG)

# TODO: Change global variable names to make them start with g_, as to show that they are global.

# Configure Flask app
app = Flask(__name__)
app.secret_key = "dd9fadd2de6003bf66cbe5ecdb6551015150fd955811ba1e8217d76c21f5f974" #os.environ.get("SECRET_KEY")


# Configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

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
app.config["MAIL_SERVER"] = 'mail.privateemail.com'
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
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

# Configure CAPTCHA
app.config['CAPTCHA_ENABLE'] = True
app.config['CAPTCHA_LENGTH'] = 5
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 60
captcha = FlaskSessionCaptcha(app)

# Configure CSRF
csrf(app)



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

	list_complete = []

	for show in list_shows:
		graves_count = Characters.query.filter_by(show_id=show.id).count()
		if graves_count > 0:
			list_complete.append(show)

	return render_template("index.html", title="OSGA: One Site to Grieve them All", shows=list_complete)


#--------------------------------------------------------------------------------------------------
###################
# FOOTER FEATURES #
###################

@app.route("/about")
def about():
	""" About page """
	return render_template("about.html", title="OSGA: One Site to Grieve them All")


@app.route("/contribute")
def contribute():
	""" Contribute page """
	return render_template("contribute.html", title="OSGA: One Site to Grieve them All")


@app.route("/terms")
def terms():
	""" Terms and conditions """
	return render_template("terms.html", title="OSGA: One Site to Grieve them All")

@csrf_exempt
@app.route("/contact", methods=["GET", "POST"])
def contact():
	""" Terms and conditions """

	error_message = ""

	if request.form.get("email") or request.form.get("subject") or request.form.get("message"):

		if captcha.validate():

			if request.form.get("email") and request.form.get("subject") and request.form.get("message"):

				admins = Users.query.filter(Users.admin_level > 0).all()
				admins_email = [admin.email for admin in admins]

				sent_email = escape(request.form.get("email"))
				sent_subject = escape(request.form.get("subject"))
				sent_message = escape(request.form.get("message"))

				msg = Message("[OSGA - Message sent by: " + sent_email + "] "+ sent_subject, sender="staff@osga-cemetery.com", recipients=admins_email)
				msg.html = sent_message
				mail.send(msg)
				return render_template("layout_message.html", title="OSGA: One Site to Grieve them All", message="Your message has been sent to our staff and we will read it as soon as we receive it. Thanks for contacting us!")

			else:
				error_message += "Please fill all the fields before submitting! "

		else:
		    error_message += "The CAPTCHA verification didn't work, please try again!"

	return render_template("contact.html", title="OSGA: One Site to Grieve them All", error=error_message, email=request.form.get("email"), subject=request.form.get("subject"), message=request.form.get("message"))


#--------------------------------------------------------------------------------------------------
#######################
# DATABASE MAGANEMENT #
#######################

@app.route("/create_db")
def create_db():
	""" Creates tables based on db.model inherited classes in models.py """
	#current_user.admin_level > 1 and g_is_local is True:
	db.create_all()
	return "Database created."

# else:
# 	abort(404)


@app.route("/empty_db")
def empty_db():
	""" Deletes all tables and data in database, resets user session """
	if current_user.is_authenticated() and current_user.admin_level > 1 and g_is_local is True:
		db.drop_all()
		current_user.name = None
		current_user.id = None
		return "Database emptied."

	else:
		abort(404)
	

@app.route("/import_shows")
def import_shows_to_db():
	""" Reads CSV file and imports shows to database """
	if current_user.is_authenticated() and current_user.admin_level > 1 and g_is_local is True:
		shows = ShowsList("Shows.csv")
		message = shows.import_shows()
		return message

	else:
		abort(404)

@app.route("/import_characters")
def import_to_db():
	""" Reads CSV file and imports characters to database """
	if current_user.is_authenticated() and current_user.admin_level > 1 and g_is_local is True:
		characters = CharactersList("Characters.csv")
		message = characters.import_characters()
		return message

	else:
		abort(404)


@app.route("/get_shows_list")
def get_shows_list():
	""" Returns a shows list in JSON format """
	show_query = Shows.query.order_by(Shows.name).all()
	shows_list = []

	for show in show_query:
		graves_count = Characters.query.filter_by(show_id=show.id).count()
		if graves_count > 0:
			show_item = { "id": show.id, "name": show.name }
			shows_list.append(show_item)

	return json.dumps(shows_list)


#--------------------------------------------------------------------------------------------------
######################
# CEMETARIES: ROUTES #
######################

@csrf_exempt
@app.route("/search_cemetery", methods=["GET", "POST"])
def search_cemetery():
	""" Searches show among shows with a cemetery in database """

	show_name = request.form.get("cemetery_search")
	show_query = Shows.query.filter_by(name=show_name)

	if show_query.count() > 0:
		return redirect(f"/cemetery/{ show_query.first().id }")

	return render_template("layout_message.html", title="OSGA: One Site to Grieve them All", error="There is no cemetery for this show (yet)!")


@app.route("/cemetery/<int:cemetery_id>", methods=["GET", "POST"])
def cemetery(cemetery_id):
	""" Displays cemetery """

	show_query = Shows.query.filter_by(id=cemetery_id).first()

	if show_query is None:
		return redirect("/")

	if request.form.get("graves_sorting") == "popularity":
		cemetery_query = Characters.query.filter_by(show_id=cemetery_id).order_by(Characters.flower_count.desc())
	
	else:
		cemetery_query = Characters.query.filter_by(show_id=cemetery_id).order_by(Characters.death_season, Characters.death_episode)


	for character in cemetery_query:
		quick_sort_flowers(character.flowers, 0, len(character.flowers) - 1)

	if current_user is None or current_user.is_authenticated is False:
		is_blocked = False
		is_spoiler = False
	else:
		is_blocked = current_user.blocked
		spoiler_query = BlacklistedShows.query.filter(and_(BlacklistedShows.user_id == current_user.id, BlacklistedShows.show_id == cemetery_id)).first()
		is_spoiler = (spoiler_query != None)

	page_title = "OSGA - " + show_query.name + "'s' Cemetery"

	return render_template("cemetery.html", title=page_title, graves_count=cemetery_query.count(), characters=cemetery_query.all(), show_title=show_query.name, show_id=show_query.id, is_blocked=is_blocked, is_spoiler=is_spoiler)


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
	show_characters = Characters.query.filter_by(show_id=show.id).order_by(Characters.id)

	if current_user is None or current_user.is_authenticated is False:
		is_spoiler = False
	else:
		spoiler_query = BlacklistedShows.query.filter(and_(BlacklistedShows.user_id == current_user.id, BlacklistedShows.show_id == show.id)).first()
		is_spoiler = (spoiler_query != None)

	return render_template("character.html", title="OSGA: One Site to Grieve them All", character=character, show=show, is_spoiler=is_spoiler, show_characters=show_characters)


@app.route("/delete_character_message/<int:message_id>", methods=["GET"])
def delete_character_message(message_id):
	""" Deletes CharactersMessage with id message_id """

	message = CharactersMessages.query.get(message_id)
	
	if current_user.is_authenticated and current_user.id == message.user_id:
		db.session.delete(message)
		db.session.commit()

	return


#--------------------------------------------------------------------------------------------------
####################
# CEMETARIES: AJAX #
####################

@csrf_exempt
@app.route("/save_flower", methods=["GET", "POST"])
def save_flower():
	""" Saves the flower with flowertype flowertype_id and position (pos_x, pos_y) in database for character character_id. """

	user_id = None

	message = request.get_json()
	character_id = message.get("character_id")
	flowertype_id = message.get("flowertype_id")
	pos_x = message.get("pos_x")
	pos_y = message.get("pos_y")
	
	# Just in case the user tried to artificially insert JS to bypass blocked account and leave flower (idk who would do that, but who knows)
	if current_user.is_authenticated:
		user = Users.query.get(current_user.id)
		if user.blocked:
			return ""

		user_id = user.id

	curr_char = Characters.query.get(character_id)

	if (curr_char.flower_count < 2147483647): # Max integer value
		curr_char.flower_count = curr_char.flower_count + 1

		flower_count_query = CharactersFlowers.query.filter(and_(CharactersFlowers.character_id == character_id, CharactersFlowers.user_id == None))

		if flower_count_query.count() > 99:
			db.session.delete(flower_count_query.first())

		db.session.add(CharactersFlowers(flowertype_id=flowertype_id, character_id=character_id, pos_x=pos_x, pos_y=pos_y, user_id=user_id))	
		db.session.commit()
	
	return ""

@csrf_exempt
@app.route("/save_message", methods=["POST"])
@login_required
def save_message():
	""" Saves message sent via POST in database. """

	# Just in case the user tried to artificially insert JS to bypass blocked account and leave message
	if (current_user.blocked):
		return ""

	message = request.get_json()
	message_content = message.get("message")
	character_id = message.get("character_id")
	db.session.add(CharactersMessages(user_id=current_user.id, character_id=character_id, content=message_content))
	db.session.commit()
	return message
	
#--------------------------------------------------------------------------------------------------
########################
# REGISTER / LOGIN-OUT #
########################

# Register
@csrf_exempt
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
		read_terms = not (request.form.get("read_terms") is None)
		error = ""

		# NOTE: isalnum() was used here to force usernames to contain only alphanumeric characters in order to protect against SQL injections,
		# but SQLAlchemy already makes them technically impossible, so this is probably not necessary.
		if not username.isalnum():
			username = ""
			error += "Your username can only contain letters or numbers. "
		
		username_exist_query = Users.query.filter_by(name=username).count()
		if username_exist_query > 0:
			username = ""
			error += "This username is already taken! "
		
		if len(password) < 8:
			password = ""
			error += "Your password must be at least 8 characters long. "	

		if password != password_confirmation:
			password = ""
			password_confirmation = ""
			error += "Password and confirmation didn't match! "

		# TODO: check email validity. Library? Regex?
		if email != email_confirmation:
			email = ""
			email_confirmation = ""
			error += "Email and confirmation didn't match! "

		email_exist_query = Users.query.filter_by(email=email).count()
		if email_exist_query > 0:
			error += "This email address is already taken!"

		if read_terms is False:
			error += "You can't register if you don't accept the terms and conditions! "

		if not captcha.validate():
			error += "The CAPTCHA verification didn't work, please try again. "

		if error != "":
			return render_template("register.html", title="OSGA: One Site to Grieve them All", error=error, username=username, password=password, password_confirmation=password_confirmation, email=email, read_terms=read_terms)

		password_salt = os.urandom(64).hex()[64:]
		password_hash = scrypt.hash(password, password_salt).hex()[64:]

		activation_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
		activation_date = datetime.now()
		activation_latest = activation_date + timedelta(days=2)

		new_user = Users(name=username, password=password_hash, password_salt=password_salt, email=email, activation_code=activation_code, activation_timelimit=activation_latest)
		db.session.add(new_user)
		db.session.commit()

		confirmation_message_title = f"Registration on OSGA"
		confirmation_message_html = f"Hello { username },<br><br>Thank you for registering on OSGA!<br><br>Your activation code is: <b>{ activation_code }</b> (valid for 2 days). \
		Fill it in on the confirmation page to activate your account!<br>Can't find the confirmation page? <a href=\"http://www.osga-cemetery.com/confirm_registration\">Click here</a>!<br><br>We hope you have a good time on our site,<br><br>The OSGA maitenance team"
		msg = Message(confirmation_message_title, sender="staff@osga-cemetery.com", recipients=[email])
		msg.html = confirmation_message_html
		mail.send(msg)

		return render_template("confirm_registration.html", email=email, message="Thank you for registering. Your account has been created! You can now log-in and get access to more features.")
	
	return render_template("register.html", title="OSGA: One Site to Grieve them All")



@csrf_exempt
@app.route("/login", methods=["GET", "POST"])
def login():
	""" Logs user in and redirects to currently visited page """

	if request.form.get("username") and request.form.get("password"):

		username_input = request.form.get("username")
		password_input = request.form.get("password")

		# NOTE: isalnum() was used here to force usernames to contain only alphanumeric characters in order to protect against SQL injections,
		# but SQLAlchemy already makes them technically impossible, so this is probably not necessary.
		if username_input.isalnum():
			login_request = Users.query.filter(and_(Users.name == username_input)).first()

			if login_request is None:
				return render_template("layout_message.html", title="OSGA: One Site to Grieve them All", error="This username doesn't exist in our database.")

			password_input_hash = scrypt.hash(password_input, login_request.password_salt).hex()[64:]
			
			if password_input_hash != login_request.password:
				return render_template("layout_message.html", title="OSGA: One Site to Grieve them All", error="Your username and password didn't match.")

			
			else:
				if login_request.activated is False:
					return render_template("confirm_registration", title="OSGA: One Site to Grieve them All", email=login_request.email)

				user = login_request
				login_user(user, remember = not (request.form.get("remember_me") is None))
			
	return redirect("/")


@app.route("/logout", methods=["GET", "POST"])
def logout():
	""" Logs user out and redirects to currently visisted page """
	logout_user()
	return redirect("/")
			

@csrf_exempt
@app.route("/confirm_registration", methods=["GET", "POST"])
def confirm_registration():

	email = request.form.get("email")

	if email is not None:
		
		user = Users.query.filter_by(email=email).first()


		if request.form.get("resend"):

			activation_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
			activation_date = datetime.now()
			activation_latest = activation_date + timedelta(days=2)

			user.activation_code = activation_code
			user.activation_timelimit = activation_latest
			db.session.commit()

			confirmation_message_title = f"Activation code for OSGA"
			confirmation_message_html = f"Hello { username },<br><br>If you haven't requested a new activation code, please ignore this email!<br><br> Your new activation code is: <b>{ activation_code }</b> (valid until: { activation_latest.time() }. Fill it in on the confirmation page to activate your account!"
			msg = Message(confirmation_message_title, sender="staff@osga-cemetery.com", recipients=[email])
			msg.html = confirmation_message_html
			mail.send(msg)

			return render_template("confirm_registration.html", title="OSGA: One Site to Grieve them All", email=email)

		# current_date needs to be timezozne aware to be compared
		timezone = user.activation_timelimit.tzinfo
		current_date = datetime.now(timezone)

		if current_date > user.activation_timelimit:
			return render_template("confirm_registration.html", title="OSGA: One Site to Grieve them All", error="Your activation code has expired! Please click on Resend here under to get a new one.", email=request.form.get("email"), resend=True)


		activation_code = request.form.get("activation_code")
		
		if activation_code == user.activation_code:
			user.activated = True
			db.session.commit() 
			login_user(user)
			return render_template("confirm_registration.html", title="OSGA: One Site to Grieve them All", success="Your account has been activated! You can now manage your account and leave message and have access to all user features.")

		else:
			return render_template("confirm_registration.html", title="OSGA: One Site to Grieve them All", error="Your activation didn't match your email address. Please check it again!", email=email)


	return render_template("confirm_registration.html", title="OSGA: One Site to Grieve them All", email=email)
	

@csrf_exempt
@app.route("/new_password", methods=["GET", "POST"])
def new_password():

	email = request.form.get("email")

	if email is not None:
		
		user = Users.query.filter_by(email=email).first()

		if user is None:
			return render_template("new_password.html", title="OSGA: One Site to Grieve them All", email="E-mail address", error="There is no user with this e-mail address on OSGA.")

		password = request.form.get("password")
		password_confirmation = request.form.get("password_confirmation")

		if password is None:

			activation_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
			activation_date = datetime.now()
			activation_latest = activation_date + timedelta(days=2)

			user.activation_code = activation_code
			user.activation_timelimit = activation_latest
			db.session.commit()

			confirmation_message_title = f"New password confirmation code for OSGA"
			confirmation_message_html = f"Hello { user.name },<br><br>If you haven't requested a password change, please ignore this email!<br><br> Your confirmation code is: <b>{ activation_code }</b>. Fill it in on the confirmation page to create a new password!"
			msg = Message(confirmation_message_title, sender="staff@osga-cemetery.com", recipients=[email])
			msg.html = confirmation_message_html
			mail.send(msg)

			return render_template("new_password.html", title="OSGA: One Site to Grieve them All", email=email, resent=True)

		# current_date needs to be timezone aware to be compared
		timezone = user.activation_timelimit.tzinfo
		current_date = datetime.now(timezone)

		if current_date > user.activation_timelimit:
			return render_template("new_password.html", title="OSGA: One Site to Grieve them All", error="Your activation code has expired! Please click on Resend here under to get a new one.", email=request.form.get("email"), resent=True)


		activation_code = request.form.get("activation_code")
		
		if activation_code == user.activation_code:
			password_salt = os.urandom(64).hex()[64:]
			password_hash = scrypt.hash(password, password_salt).hex()[64:]
			user.password_salt = password_salt
			user.password = password_hash
			db.session.commit() 
			login_user(user)
			return render_template("new_password.html", title="OSGA: One Site to Grieve them All", success="You password has successfully been changed!")

		else:
			return render_template("new_password.html", title="OSGA: One Site to Grieve them All", error="Your confirmation code didn't match your email address. Please check it again!", email=email, resent=True)


	return render_template("new_password.html", title="OSGA: One Site to Grieve them All", email="E-mail address")

#--------------------------------------------------------------------------------------------------
#############
# USER INFO #
#############

@csrf_exempt
@app.route("/user_panel", methods=["GET"])
@login_required
def user_panel_default():
	""" Returns default user panel tab """	
	return user_panel("")


@csrf_exempt
@app.route("/user_panel/<string:page_type>", methods=["GET", "POST"])
@login_required
def user_panel(page_type):
	""" Returns specified user panel page if it exists, otherwise default. """

	if current_user.id is None:
		return redirect("/")

	user = Users.query.get(current_user.id)
	error_message = ""
	success_message = ""
	new_email = False
	new_email_address = ""

	#---- Display User settings tab ----#
	if page_type == "user_settings": 
		if request.form.get("password"):
			if request.form.get("password") != request.form.get("password_confirmation"):
				error_message += "Password and password confirmation didn't match! "
			elif len(request.form.get("password")) < 8:
				error_message += "Password should be at least 8 characters long. "
			elif login_fresh() is False:
				error_message += "You are using an old session, please log out and log in again to change your password."
			else:
				success_message += "Your password has been changed! "
				
				user.password_salt = base64.b64encode(os.urandom(64))[64:]
				user.password = base64.b64encode(scrypt.hash(password, user.password_salt))[64:]
				db.session.commit()
		
		###  E-mail Change  ###
		if request.form.get("email"):

			new_email_address = request.form.get("email")
			email_exist_query = Users.query.filter_by(email=new_email_address).count()

			if new_email_address != request.form.get("email_confirmation"):
				error_message += "E-mail address and confirmation didn't match! "

			elif login_fresh() is False:
				error_message += "You are using an old session, please log out and log in again to change your e-mail address."

			elif email_exist_query > 0:
				error_message += "This email address is already taken!"

			elif request.form.get("email_confirmation_code"):
				# current_date needs to be timezozne aware to be compared
				timezone = user.activation_timelimit.tzinfo
				current_date = datetime.now(timezone)

				if current_date > user.activation_timelimit:
					error_message += "Your activation code has expired! Please click on Resend here under to get a new one."

				else:
					activation_code = request.form.get("email_confirmation_code")
					
					if activation_code == user.activation_code:
						user.email = new_email_address
						db.session.commit() 
						login_user(user)
						success_message += "Your email has successfully been updated!"

					else:
						error_message += "Your confirmation code didn't work, try copy-pasting it from your confirmation e-mail!"
						new_email = True

			else:
				activation_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
				activation_date = datetime.now()
				activation_latest = activation_date + timedelta(days=2)
				
				user.activation_code = activation_code
				user.activation_timelimit = activation_latest
				db.session.commit() 
					
				confirmation_message_title = f"New e-mail address on OSGA"
				confirmation_message_html = f"Hello { user.name },<br><br>Your request to change your e-mail address on OSGA has been received!<br><br>Your confirmation code is: <b>{ activation_code }</b> (valid for 2 days). \
				Fill it in on the user panel!<br><br>We hope you have a good time on our site,<br><br>The OSGA maitenance team"
				msg = Message(confirmation_message_title, sender="staff@osga-cemetery.com", recipients=[new_email_address])
				msg.html = confirmation_message_html
				mail.send(msg)

				success_message += "Your request to change your e-mail address has been taken into account. In order to control that you entered a valid e-mail address, we sent \
				you a confirmation e-mail. Please add the confirmation code you received via email under your e-mail address in the form hereunder!"

				new_email = True


		if request.form.get("update_pref"):
			user.display_fav = not (request.form.get("display_favourite") is None)
			user.display_activity = not (request.form.get("display_activity") is None)
			db.session.commit()

		return render_template("user_panel.html", title="OSGA: One Site to Grieve them All", selected_user_settings="active", user_info=user, error=error_message, success=success_message, fresh_session=login_fresh(), new_email=new_email, new_email_address=new_email_address)


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

		return render_template("user_panel.html", title="OSGA: One Site to Grieve them All", selected_suggestions="active", error=confirmation)


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
	blacklist = []

	if not user_profile:
		return redirect(request.referrer)

	if user_profile.display_fav:
		user_favourite = Shows.query.join(FavouritedShows, FavouritedShows.show_id == Shows.id, isouter=True).filter(FavouritedShows.user_id == user_profile.id)
	
	activity_total = []	
	activity_total = user_profile.flowers + user_profile.messages
	activity_total.sort(key=lambda x: x.date, reverse=True)

	for act in activity_total:
		if isinstance(act, CharactersFlowers):
			act.type = "flower"
		else:
			act.type = "message"

	if current_user is True:		
		blacklisted_shows = BlacklistedShows.query.filter_by(user_id=current_user.id)
		for show in blacklisted_shows:
			blacklist.append(show.id)

	page_title = "OSGA - " + user_profile.name + "'s profile"
	return render_template("user_profile.html", title=page_title, user_profile_name=user_profile.name, user_profile_favourite_shows=user_favourite, activity=activity_total[:50], blacklist=blacklist)



#--------------------------------------------------------------------------------------------------
##################
# ADMINISTRATION #
##################

@app.route("/admin_panel", methods=["GET"])
@login_required
def admin_panel_default():
	""" Returns default admin panel tab """
	return admin_panel("")


@csrf_exempt
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

			message=f"{ character } has been declared dead on season { season } episode { episode }. Their grave has been added to { show_title }'s cemetery."	

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




@csrf_exempt
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



@csrf_exempt
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