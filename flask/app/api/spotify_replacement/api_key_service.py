from app.main import db
from .database.models import ApiKey
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

class ApiKeyService:
    @staticmethod
    def create_key(name: str, rate_limit: int = 1000) -> ApiKey:
        """Create a new API key"""
        api_key = ApiKey(
            key=ApiKey.generate_key(),
            name=name,
            rate_limit=rate_limit
        )
        db.session.add(api_key)
        db.session.commit()
        return api_key

    @staticmethod
    def get_key(key: str) -> Optional[ApiKey]:
        """Get an API key by its value"""
        return ApiKey.query.filter_by(key=key).first()

    @staticmethod
    def validate_key(key: str) -> bool:
        """Validate an API key and update its usage"""
        api_key = ApiKeyService.get_key(key)
        if not api_key or not api_key.is_active:
            return False

        # Update last used time and request count
        api_key.last_used_at = datetime.now(timezone.utc)
        api_key.request_count += 1
        db.session.commit()
        return True

    @staticmethod
    def list_keys() -> List[ApiKey]:
        """List all API keys"""
        return ApiKey.query.all()

    @staticmethod
    def deactivate_key(key: str) -> bool:
        """Deactivate an API key"""
        api_key = ApiKeyService.get_key(key)
        if api_key:
            api_key.is_active = False
            db.session.commit()
            return True
        return False

    @staticmethod
    def reset_count(key: str) -> bool:
        """Reset the request count for an API key"""
        api_key = ApiKeyService.get_key(key)
        if api_key:
            api_key.request_count = 0
            db.session.commit()
            return True
        return False 