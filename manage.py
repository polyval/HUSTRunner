from flask_script import Manager, Server, Shell
from app import create_app, db
from app.user.models import User, Role
from app.forum.models import Post, Topic


app = create_app('testing')
manager = Manager(app)


def make_shell_context():
    """Return a dict of objects
    eg:
        >> python manage.py shell
        >> app
        <Flask 'app'>
    """
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Topic=Topic)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    # find all test files
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()