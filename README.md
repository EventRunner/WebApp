# WebApp
Web Interface for VENT

PEOPLE

Jon, Jacob, Owen, Warfa (in order of impotence)


TECHNOLOGY

Flask, jQuery, Bootstrap, SQLite, SQLAlchemy (through flask-sqlalchemy), Alembic (through flask-migrate)


TOOLS

bootsnipp.com

http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

SQLiteman


SETUP

Install Python and pip. Then use:
pip install -r requirements.txt


USAGE

python server.py - runs server on localhost:5000

python manage.py runserver - runs server on localhost:5000

python manage.py db init - initializes app.db based on models.py (need to run an upgrade after)

python manage.py db migrate - creates migration file after models.py has been modified

python manage.py db upgrade - applies most recent migration file

