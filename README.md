To recreate the db files:
run in terminal:
    python migrate.py db init

to change db configuration:
change models.py configuration
run in terminal:
    python migrate.py db migrate
    python migrate.py db upgrade
