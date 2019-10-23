import os
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
# from app.models import User, Role
from flask_script import Manager, Shell

app = create_app('default')
# app = Flask(__name__)
migrate = Migrate(app, db)
manager = Manager(app)

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)

# manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)



