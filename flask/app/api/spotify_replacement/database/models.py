from app.main import db
from datetime import datetime, timezone
import secrets

class ApiKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    rate_limit = db.Column(db.Integer, default=1000)  # requests per day
    request_count = db.Column(db.Integer, default=0)

    @staticmethod
    def generate_key():
        return secrets.token_urlsafe(32)

    def __repr__(self):
        return f"<ApiKey {self.name}>" 