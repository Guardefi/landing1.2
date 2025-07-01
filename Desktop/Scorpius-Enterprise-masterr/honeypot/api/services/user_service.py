"""
User management service for API key management
"""
import logging
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

from database.mongodb_client import MongoDBClient

# Configure logger
logger = logging.getLogger("api.services.user_service")


class UserService:
    """Service for managing users and API keys"""

    def __init__(self, mongo_client: MongoDBClient):
        """Initialize user service with MongoDB client"""
        self.mongo_client = mongo_client
        self.collection_name = "users"

    @property
    def collection(self):
        """Get MongoDB collection"""
        return self.mongo_client.db[self.collection_name]

    async def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get user by API key

        Args:
            api_key: API key to look up

        Returns:
            User document or None if not found
        """
        try:
            return await self.collection.find_one({"api_key": api_key})
        except Exception as e:
            logger.error(f"Error getting user by API key: {e}", exc_info=True)
            return None

    async def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key

        Args:
            api_key: API key to validate

        Returns:
            True if valid, False otherwise
        """
        user = await self.get_user_by_api_key(api_key)
        return user is not None and not user.get("is_disabled", False)

    async def get_rate_limit(self, api_key: str) -> int:
        """
        Get rate limit for API key

        Args:
            api_key: API key

        Returns:
            Rate limit (requests per minute)
        """
        user = await self.get_user_by_api_key(api_key)
        return user.get("rate_limit", 100) if user else 100

    async def create_user(
        self, username: str, email: str, is_admin: bool = False, rate_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Create new user with generated API key

        Args:
            username: Username
            email: Email address
            is_admin: Whether user has admin privileges
            rate_limit: API rate limit

        Returns:
            Created user document
        """
        try:
            # Check if user already exists
            existing_user = await self.collection.find_one(
                {"$or": [{"username": username}, {"email": email}]}
            )

            if existing_user:
                raise ValueError(f"User already exists with username or email")

            # Generate API key
            api_key = secrets.token_urlsafe(32)

            # Create user document
            user = {
                "username": username,
                "email": email,
                "api_key": api_key,
                "is_admin": is_admin,
                "rate_limit": rate_limit,
                "is_disabled": False,
                "created_at": datetime.utcnow(),
            }

            # Insert into database
            result = await self.collection.insert_one(user)
            user["_id"] = result.inserted_id

            logger.info(f"Created new user: {username}")
            return user

        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise

    async def regenerate_api_key(self, user_id: str) -> Optional[str]:
        """
        Regenerate API key for user

        Args:
            user_id: User ID

        Returns:
            New API key or None if error
        """
        try:
            # Generate new API key
            new_api_key = secrets.token_urlsafe(32)

            # Update in database
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"api_key": new_api_key, "updated_at": datetime.utcnow()}},
            )

            if result.modified_count == 1:
                logger.info(f"Regenerated API key for user {user_id}")
                return new_api_key
            else:
                return None

        except Exception as e:
            logger.error(f"Error regenerating API key: {e}", exc_info=True)
            return None

    async def disable_user(self, user_id: str) -> bool:
        """
        Disable user

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"is_disabled": True, "updated_at": datetime.utcnow()}},
            )

            success = result.modified_count == 1
            if success:
                logger.info(f"Disabled user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Error disabling user: {e}", exc_info=True)
            return False

    async def enable_user(self, user_id: str) -> bool:
        """
        Enable user

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"is_disabled": False, "updated_at": datetime.utcnow()}},
            )

            success = result.modified_count == 1
            if success:
                logger.info(f"Enabled user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Error enabling user: {e}", exc_info=True)
            return False

    async def update_rate_limit(self, user_id: str, rate_limit: int) -> bool:
        """
        Update user rate limit

        Args:
            user_id: User ID
            rate_limit: New rate limit

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"rate_limit": rate_limit, "updated_at": datetime.utcnow()}},
            )

            success = result.modified_count == 1
            if success:
                logger.info(f"Updated rate limit for user {user_id} to {rate_limit}")

            return success

        except Exception as e:
            logger.error(f"Error updating rate limit: {e}", exc_info=True)
            return False

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all users

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user documents
        """
        try:
            cursor = (
                self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
            )
            return await cursor.to_list(length=limit)

        except Exception as e:
            logger.error(f"Error getting users: {e}", exc_info=True)
            return []
