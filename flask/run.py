#!/usr/bin/env python

import os
from app import create_app, db
from dotenv import load_dotenv
from flask_migrate import upgrade
import subprocess

from app import create_app, bootstrap_app

# edit for sqlite
from app.utils.app import wait_for_db_connection, get_migrations_dir, get_dot_env_path
from app.utils.app import get_migrations_dir, get_dot_env_path
from app.config.sqlalchemy import config_database_extensions


dotenv_path = get_dot_env_path()
load_dotenv(dotenv_path)

# edit for sqlite
# This if statement assures that the upgrades are only run once
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    wait_for_db_connection()

# The app must be created after the db connection is established
app = create_app()

# Configure database extensions for all tenants
with app.app_context():
    config_database_extensions(db)

# This if statement assures that the upgrades are only run once
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    with app.app_context():
        upgrade(directory=get_migrations_dir("migrations"))

    os.system('pybabel compile -d app/translations')
    
bootstrap_app(app)


if os.environ.get("APP_ENV") != "dev":
    from uwsgidecorators import postfork

    @postfork
    def reset_db_connections():
        # Whenever we create a flask application (in the uwsgi master process), the SQLALCHEMY_BINDS leads flask to create a single enigne for each tenant
        # When we fork the master process to create the workers, they will be sharing the same engines, which will cause concurrency issues
        # (let's not forget the errors we spent so much time debugging)
        # To avoid these issues, we need to dispose the connection pool for each worker
        # Whenever we dispose an engine, a new connection pool is immediately created:
        #   https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Engine.dispose
        with app.app_context():
            for e in db.engines.values():
                e.dispose()
            db.engine.dispose()


@app.shell_context_processor
def make_shell_context():

    return dict(
        db=db,
    )


if __name__ == "__main__":
    subprocess.run(["flask", "run", "--host=0.0.0.0"])
