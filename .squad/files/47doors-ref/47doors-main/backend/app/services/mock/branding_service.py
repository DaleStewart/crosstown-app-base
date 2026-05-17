"""
Mock branding service for testing and demo mode.
Stores branding configuration in memory.
"""

from datetime import datetime, timezone
from typing import Optional

from app.models.schemas import BrandingConfig
from app.services.interfaces import BrandingServiceInterface


class MockBrandingService(BrandingServiceInterface):
    """Mock implementation of branding service using in-memory storage."""

    # Class-level storage to persist across requests
    _branding: Optional[BrandingConfig] = None

    @classmethod
    def _get_default_branding(cls) -> BrandingConfig:
        """Get default branding configuration."""
        return BrandingConfig(
            logo_url=None,
            primary_color="#2563eb",
            institution_name="University Support",
            tagline="Get help with IT, registration, financial aid, and more",
            updated_at=datetime.now(timezone.utc),
        )

    async def get_branding(self) -> BrandingConfig:
        """Get current branding configuration."""
        if MockBrandingService._branding is None:
            MockBrandingService._branding = self._get_default_branding()
        return MockBrandingService._branding

    async def update_branding(
        self,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        institution_name: Optional[str] = None,
        tagline: Optional[str] = None,
    ) -> BrandingConfig:
        """Update branding configuration. Only provided fields are updated."""
        current = await self.get_branding()

        # Update only provided fields
        updated = BrandingConfig(
            logo_url=logo_url if logo_url is not None else current.logo_url,
            primary_color=primary_color if primary_color is not None else current.primary_color,
            institution_name=institution_name if institution_name is not None else current.institution_name,
            tagline=tagline if tagline is not None else current.tagline,
            updated_at=datetime.now(timezone.utc),
        )

        MockBrandingService._branding = updated
        return updated

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 1, None

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Reset branding to defaults (for testing)."""
        cls._branding = None
