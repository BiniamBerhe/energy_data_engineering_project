import click
from flask.cli import with_appcontext
from app import create_app, db

app = create_app()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo("Initialized the database.")


app.cli.add_command(init_db_command)

if __name__ == "__main__":
    app.run(debug=True)
