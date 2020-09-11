from flask_script import Manager
from App.__init__ import create_app
from flask_migrate import MigrateCommand

# 调用
app = create_app()
manage = Manager(app)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()
