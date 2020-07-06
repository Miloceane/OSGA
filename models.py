################################
# OSGA - models.py  	       #
# Written by Charlotte Lafage  #
# (GitHub: Miloceane)          #
# For Minor Programmeren       #
# (Universiteit van Amsterdam) #
################################

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

db = SQLAlchemy()

class Users(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	password = db.Column(db.String(128))
	email = db.Column(db.String(128))
	admin_level = db.Column(db.Integer, default=0)
	registration_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
	display_fav = db.Column(db.Boolean, default=False)
	display_activity = db.Column(db.Boolean, default=False)
	flowers_left = db.Column(db.Integer, default=5)
	blocked = db.Column(db.Boolean, default=False)
	# authenticated = db.Column(db.Boolean, default=False)

	def is_authenticated(self):
		return True


	def is_active(self):
		return True


	def is_anonymous(self):
		return False


	def get_id(self):
		return(self.id) 



class Universes(db.Model):
	__tablename__ = 'shows_universes'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))


class Shows(db.Model):
	__tablename__ = 'shows'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	universe_id = db.Column(db.Integer, db.ForeignKey('shows_universes.id')) 
	api_id = db.Column(db.String(128)) 


class FavouritedShows(db.Model):
	__tablename__ = 'shows_favourited'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
	show_id = db.Column(db.Integer, db.ForeignKey('shows.id')) 
 

class BlacklistedShows(db.Model):
	__tablename__ = 'shows_blacklisted'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
	show_id = db.Column(db.Integer, db.ForeignKey('shows.id'))


class FlowerTypes(db.Model):
	__tablename__ = 'flower_types'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	user_lvl = db.Column(db.Integer)

class CharactersMessages(db.Model):
	__tablename__ = 'characters_messages'
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime(timezone=True), server_default=func.now())
	content = db.Column(db.String(128))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
	character_id = db.Column(db.Integer, db.ForeignKey('characters.id')) 
	admin_id = db.Column(db.Integer, default=0) # Admin who validated the message 
	pos_x =  db.Column(db.Integer, default=0)
	pos_y =  db.Column(db.Integer, default=0)	
	character = relationship("Characters", back_populates="messages")

class CharactersFlowers(db.Model):
	__tablename__ = 'characters_flowers'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	flowertype_id = db.Column(db.Integer)# , db.ForeignKey('flower_types.id'))  -> For some reason, complained about there being no constraints?
	character_id = db.Column(db.Integer, db.ForeignKey('characters.id')) 
	date = db.Column(db.DateTime(timezone=True), server_default=func.now())
	pos_x =  db.Column(db.Integer)
	pos_y =  db.Column(db.Integer)	
	character = relationship("Characters", back_populates="flowers")

class Characters(db.Model):
	__tablename__ = 'characters'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	universe_id = db.Column(db.Integer, db.ForeignKey('shows_universes.id')) 
	show_id = db.Column(db.Integer, db.ForeignKey('shows.id'))
	death_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
	death_season = db.Column(db.Integer)
	death_episode = db.Column(db.Integer)
	admin_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Admin who declared death
	flower_count = db.Column(db.Integer)
	flowers = relationship(CharactersFlowers)
	messages = relationship(CharactersMessages)




class Suggestions(db.Model):
	__tablename__ = 'suggestions'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	date = db.Column(db.DateTime(timezone=True), server_default=func.now())
	show = db.Column(db.String(128))
	content = db.Column(db.String(512))
	is_read = db.Column(db.Boolean, default=False)
	is_important = db.Column(db.Boolean, default=False)	