from flask_script import Manager, Server, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.user.models import User, Role, Follow
from app.forum.models import Post, Topic, Comment
from app.message.models import Notification, NotifyConfig
from app.activity.models import Activity
from app.main.models import ImgFace, Tag

app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """Return a dict of objects
    eg:
        >> python manage.py shell
        >> app
        <Flask 'app'>
    """
    return dict(app=app, db=db, User=User,
                Role=Role, Post=Post,
                Topic=Topic, Comment=Comment,
                notify=Notification,
                NotifyConfig = NotifyConfig,
                Activity=Activity,
                Img=ImgFace, Tag=Tag)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def fake():
    """Generate testing data"""
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    Topic.insert_topic()
    User.generate_fake()
    Post.generate_fake()
    Comment.generate_fake()
    Follow.generate_fake()


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    # find all test files
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def deploy():
   Role.insert_roles()
   Topic.insert_topic()


if __name__ == '__main__':
    manager.run()
