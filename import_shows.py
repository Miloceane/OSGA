import os, csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *


class ShowsList():
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

	def import_shows(self):
		# read CSV
		file = open(self.import_file)
		reader = csv.reader(file)

		query_check = Shows.query.count()
		# if query_check > 0:
		# 	return "Characters had alredy been imported!"

		for show, show_type, show_universe in reader:
			if show == "show":
				continue

			check_shows = Shows.query.filter_by(name=show)
			check_universe = Universes.query.filter_by(name=show_universe)

			if check_universe.count() == 0:
				db.session.add(Universes(name=show_universe))
				db.session.commit()

			universe = Universes.query.filter_by(name=show_universe).first()
			is_series = True if show_type == "series" else False

			if check_shows.count() == 0:
				db.session.add(Shows(name=show, universe_id=universe.id, is_series=is_series))
				db.session.commit()

		return "Shows have been imported!"


if __name__ == "__main__":
	Shows = ShowsList("Shows.csv")
	shows.fetch_default_db()
	print(shows.import_shows())
