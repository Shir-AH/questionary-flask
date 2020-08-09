To recreate the db files:
run in python console from base dir:

from questionary import create_app
app = create_app()
app.app_context().push()
from questionary import db
db.create_all()

to change db configuration:
change models.py configuration
run in terminal:
    python migrate.py db migrate
    python migrate.py db upgrade
