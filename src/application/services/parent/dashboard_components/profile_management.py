"""
👨‍👩‍👧‍👦 Profile Management Service
High cohesion component for parent and child profile operations
"""

import logging
from typing import Optional
from .models import ChildProfileData


class ProfileManagementService:
    """
    Dedicated service for parent and child profile management.
    High cohesion: all methods work with profile data and operations.
    """

    def __init__(self, orchestrator, child_repository):
        """Initialize profile management service"""
        self.orchestrator = orchestrator
        self.child_repository = child_repository
        self.logger = logging.getLogger(__name__)

    async def create_parent_account(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        timezone: str = "UTC"
    ):
        """
        Create a new parent account with validation.
        Delegates to orchestrator for business logic.
        """
        try:
            parent_user = await self.orchestrator.create_parent_account(
                email, name, phone, timezone
            )

            self.logger.info(f"Successfully created parent account: {email}")
            return parent_user

        except Exception as e:
            self.logger.error(
                f"Failed to create parent account for {email}: {e}")
            raise

    async def create_child_profile(self, profile_data: ChildProfileData):
        """
        Create child profile with age-appropriate defaults.
        Handles validation and business logic delegation.
        """
        try:
            # Validate profile data (already done in __post_init__)
            child_profile = await self.orchestrator.create_child_profile(
                profile_data.parent_id,
                profile_data.name,
                profile_data.age,
                profile_data.interests,
                profile_data.language
            )

            self.logger.info(
                f"Successfully created child profile: {profile_data.name} "
                f"(age {profile_data.age}) for parent {profile_data.parent_id}"
            )

            return child_profile

        except Exception as e:
            self.logger.error(
                f"Failed to create child profile for {profile_data.name}: {e}"
            )
            raise

    async def get_child_profile(self, child_id: str):
        """Get child profile by ID"""
        try:
            profile = await self.child_repository.get_by_id(child_id)
            if not profile:
                self.logger.warning(f"Child profile not found: {child_id}")
                return None

            return profile

        except Exception as e:
            self.logger.error(f"Failed to get child profile {child_id}: {e}")
            raise

    async def update_child_profile(
        self,
        child_id: str,
        updates: dict
    ) -> bool:
        """Update child profile information"""
        try:
            # Get existing profile
            existing_profile = await self.get_child_profile(child_id)
            if not existing_profile:
                return False

            # Update profile through repository
            success = await self.child_repository.update(child_id, updates)

            if success:
                self.logger.info(
                    f"Successfully updated child profile: {child_id}")
            else:
                self.logger.warning(
                    f"Failed to update child profile: {child_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error updating child profile {child_id}: {e}")
            return False

    async def delete_child_profile(self, child_id: str) -> bool:
        """Delete child profile (soft delete for safety)"""
        try:
            # Mark as inactive instead of hard delete
            success = await self.child_repository.update(
                child_id,
                {"active": False, "deleted_at": "now()"}
            )

            if success:
                self.logger.info(
                    f"Successfully deactivated child profile: {child_id}")
            else:
                self.logger.warning(
                    f"Failed to deactivate child profile: {child_id}")

            return success

        except Exception as e:
            self.logger.error(
                f"Error deactivating child profile {child_id}: {e}")
            return False

    async def get_children_for_parent(self, parent_id: str):
        """Get all children for a specific parent"""
        try:
            children = await self.child_repository.get_by_parent_id(parent_id)

            # Filter out inactive profiles
            active_children = [
                child for child in children
                if getattr(child, 'active', True)
            ]

            self.logger.debug(
                f"Found {len(active_children)} active children for parent {parent_id}")
            return active_children

        except Exception as e:
            self.logger.error(
                f"Failed to get children for parent {parent_id}: {e}")
            raise

    async def get_parent_by_id(self, parent_id: str):
        """Get parent user from database with validation"""
        try:
            if not isinstance(parent_id, str) or not parent_id:
                self.logger.error("Invalid parent_id for get_parent_by_id")
                return None

            # Would delegate to parent repository
            parent = await self.orchestrator.get_parent_by_id(parent_id)

            if parent:
                self.logger.debug(f"Found parent: {parent_id}")
            else:
                self.logger.warning(f"Parent not found: {parent_id}")

            return parent

        except Exception as e:
            self.logger.error(f"Error getting parent {parent_id}: {e}")
            return None

    async def update_parent_settings(
        self,
        parent_id: str,
        settings: dict
    ) -> bool:
        """Update parent account settings"""
        try:
            # Validate settings
            allowed_settings = [
                'name', 'phone', 'timezone', 'email_notifications',
                'push_notifications', 'language_preference'
            ]

            filtered_settings = {
                k: v for k, v in settings.items()
                if k in allowed_settings
            }

            if not filtered_settings:
                self.logger.warning(
                    f"No valid settings to update for parent {parent_id}")
                return False

            # Update through orchestrator
            success = await self.orchestrator.update_parent_settings(
                parent_id, filtered_settings
            )

            if success:
                self.logger.info(
                    f"Successfully updated parent settings: {parent_id}")
            else:
                self.logger.warning(
                    f"Failed to update parent settings: {parent_id}")

            return success

        except Exception as e:
            self.logger.error(
                f"Error updating parent settings {parent_id}: {e}")
            return False

    def get_profile_stats(self) -> dict:
        """Get profile management statistics"""
        return {
            "service_name": "ProfileManagementService",
            "operations": [
                "create_parent_account",
                "create_child_profile",
                "get_child_profile",
                "update_child_profile",
                "delete_child_profile",
                "get_children_for_parent",
                "get_parent_by_id",
                "update_parent_settings"
            ],
            "high_cohesion": True,
            "responsibility": "Parent and child profile management"
        }
