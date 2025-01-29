from app.api.files.integrations.aws.routes import aws_bp


blueprints = [aws_bp]


def register_routes(app):
    for b in blueprints:
        app.register_blueprint(b, url_prefix="/dev")
