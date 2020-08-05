import os, csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *


class CharactersList():
	def __init__(self, import_file):
		self.import_file = import_file
		self.database = db # db is default database from models

	def set_db(self, database):
		self.database = database

	def fetch_default_db(self):
		app = Flask(__name__)

		# Check for environment variable
		if not os.getenv("DATABASE_URL"):
			raise RuntimeError("DATABASE_URL is not set")
		# Configure session to use filesystem
		app.config["SESSION_PERMANENT"] = False
		app.config["SESSION_TYPE"] = "filesystem"
		Session(app)
		engine = create_engine(os.getenv("DATABASE_URL"))
		self.database = scoped_session(sessionmaker(bind=engine))

	def import_characters(self):
		# read CSV
		file = open(self.import_file)
		reader = csv.reader(file)

		# query_check = Characters.query.count()
		# if query_check > 0:
		# 	return "Characters had alredy been imported!"

		for series, name, season_death, episode_death in reader:
			if series == "series":
				continue

			check_series = Shows.query.filter_by(name=series)

			if check_series.count() == 0:
				db.session.add(Shows(name=series))
				db.session.commit()

			char_show = Shows.query.filter_by(name=series).first()

			char_exist = Characters.query.filter_by(name=name, show_id=char_show.id)

			if char_exist.count() == 0:
				if episode_death == "":
					episode_death = 0
				
				db.session.add(Characters(name=name, show_id=char_show.id, universe_id=char_show.universe_id, death_season=season_death, death_episode=episode_death, admin_id=session.get('user_id')))
			
			elif char_exist.first().death_episode != episode_death:
				curr_char = char_exist.first()
				curr_char.death_episode = episode_death
				db.session.commit()


		db.session.commit()
		return "Characters have been imported!"

# if __name__ == "__main__":
# 	books = BooksList("Characters.csv")
# 	books.fetch_default_db()
# 	print(books.import_books())
