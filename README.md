To recreate the db files:
run in python console from base dir:
    from flaskblog import create_app
    app = create_app()
    app.app_context().push()
    from flaskblog import db
    db.create_all()

to add a table column:
run in python terminal:
    from flaskblog import create_app
    app = create_app()
    app.app_context().push()
    from flaskblog import db
    from flaskblog.models import add_column
    column = db.Column(...)
    add_column(app, 'table name', column)
then change the table's Model accordingly.

to add a new table(s):
    write table(s) model(s) in models.py
    erase all pycache files
    recreate the db structure in python terminal
