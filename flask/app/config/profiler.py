import os
from werkzeug.middleware.profiler import ProfilerMiddleware

from .utils import as_bool


def config_profiler(app):
    profiler = as_bool(os.environ.get("APP_PROFILER"))
    if profiler:
        if not os.path.exists(os.path.join(os.getcwd(), "profiler")):
            os.mkdir(os.path.join(os.getcwd(), "profiler"))

        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            profile_dir=os.path.join(os.getcwd(), "profiler"),
            filename_format="{time}-{method}-{path}-{elapsed}.prof",
        )
