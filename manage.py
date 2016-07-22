from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    pass

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
