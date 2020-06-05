import click
from flask.cli import with_appcontext

from physicscontests import db
from physicscontests.models import User, Solved_by, Task, Contest

@click.command(name="create_tables")
@with_appcontext
def create_tables():
	db.create_all()
