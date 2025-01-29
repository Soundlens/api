
from .commands import commands_bp
from app.utils.app import import_blueprint
mandatory_blueprints = [
    commands_bp,
]


optional_modules = {
    "app.api.history.commands": ["events_commands_bp"],
    "app.api.permissions.commands": ["permission_commands_bp"],
    "app.utils.commands": ["utils_commands_bp"],
}



def register_commands(app):
    # Register mandatory blueprints statically imported

    for bp in mandatory_blueprints:
        app.register_blueprint(bp)

    # Register optional blueprints dynamically
    for module, bps in optional_modules.items():
        for bp_name in bps:
            bp = import_blueprint(module, bp_name)
            if bp:
                app.register_blueprint(bp)
