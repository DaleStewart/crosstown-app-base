"""
Dependency injection container for the Front Door Support Agent.
Provides service instances based on configuration (mock vs production).
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.interfaces import (
    AuditLogInterface,
    BrandingServiceInterface,
    KnowledgeServiceInterface,
    LLMServiceInterface,
    PhoneServiceInterface,
    RealtimeServiceInterface,
    SessionStoreInterface,
    TicketServiceInterface,
)


@lru_cache
def get_llm_service(settings: Settings | None = None) -> LLMServiceInterface:
    """Get LLM service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()
    else:
        from app.services.azure.llm_service import AzureOpenAILLMService
        # Pass API key only if explicitly set (for local dev), otherwise use managed identity
        api_key = settings.azure_openai_api_key if settings.azure_openai_api_key else None
        return AzureOpenAILLMService(
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
            api_key=api_key,
        )


@lru_cache
def get_ticket_service(settings: Settings | None = None) -> TicketServiceInterface:
    """Get ticket service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.ticket_service import MockTicketService
        return MockTicketService()
    else:
        # TODO: Implement ServiceNow service
        from app.services.mock.ticket_service import MockTicketService
        return MockTicketService()


@lru_cache
def get_knowledge_service(settings: Settings | None = None) -> KnowledgeServiceInterface:
    """Get knowledge service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.knowledge_service import MockKnowledgeService
        return MockKnowledgeService()
    else:
        from app.services.azure.knowledge_service import AzureSearchKnowledgeService
        api_key = settings.azure_openai_api_key if settings.azure_openai_api_key else None
        return AzureSearchKnowledgeService(
            search_endpoint=settings.azure_search_endpoint,
            search_key=settings.azure_search_key,
            index_name=settings.azure_search_index,
            openai_endpoint=settings.azure_openai_endpoint,
            openai_api_key=api_key,
        )


@lru_cache
def get_session_store(settings: Settings | None = None) -> SessionStoreInterface:
    """Get session store instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.session_store import MockSessionStore
        return MockSessionStore()
    else:
        # TODO: Implement Cosmos DB session store
        from app.services.mock.session_store import MockSessionStore
        return MockSessionStore()


@lru_cache
def get_audit_log(settings: Settings | None = None) -> AuditLogInterface:
    """Get audit log instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.audit_log import MockAuditLog
        return MockAuditLog()
    else:
        # TODO: Implement Cosmos DB audit log
        from app.services.mock.audit_log import MockAuditLog
        return MockAuditLog()


@lru_cache
def get_branding_service(settings: Settings | None = None) -> BrandingServiceInterface:
    """Get branding service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.branding_service import MockBrandingService
        return MockBrandingService()
    else:
        # TODO: Implement Cosmos DB branding service
        from app.services.mock.branding_service import MockBrandingService
        return MockBrandingService()


@lru_cache
def get_realtime_service(settings: Settings | None = None) -> RealtimeServiceInterface:
    """Get realtime service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.realtime import MockRealtimeService
        return MockRealtimeService()
    else:
        from app.services.azure.realtime import AzureRealtimeService
        # Pass API key only if explicitly set (for local dev), otherwise use managed identity
        api_key = settings.azure_openai_api_key if settings.azure_openai_api_key else None
        return AzureRealtimeService(
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_realtime_deployment,
            api_version=settings.azure_openai_realtime_api_version,
            api_key=api_key,
        )


@lru_cache
def get_phone_service(settings: Settings | None = None) -> PhoneServiceInterface:
    """Get phone service instance (mock or production)."""
    if settings is None:
        settings = get_settings()

    if settings.use_mock_services:
        from app.services.mock.phone import MockPhoneService
        return MockPhoneService()
    else:
        from app.services.azure.phone import AzurePhoneService
        # Use connection string if provided, otherwise fall back to managed identity
        connection_string = settings.azure_acs_connection_string if settings.azure_acs_connection_string else None
        return AzurePhoneService(
            acs_endpoint=settings.azure_acs_endpoint,
            openai_endpoint=settings.azure_openai_endpoint,
            openai_deployment=settings.azure_openai_realtime_deployment,
            connection_string=connection_string,
        )


# FastAPI dependency annotations
SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMServiceDep = Annotated[LLMServiceInterface, Depends(get_llm_service)]
TicketServiceDep = Annotated[TicketServiceInterface, Depends(get_ticket_service)]
KnowledgeServiceDep = Annotated[KnowledgeServiceInterface, Depends(get_knowledge_service)]
SessionStoreDep = Annotated[SessionStoreInterface, Depends(get_session_store)]
AuditLogDep = Annotated[AuditLogInterface, Depends(get_audit_log)]
BrandingServiceDep = Annotated[BrandingServiceInterface, Depends(get_branding_service)]
RealtimeServiceDep = Annotated[RealtimeServiceInterface, Depends(get_realtime_service)]
PhoneServiceDep = Annotated[PhoneServiceInterface, Depends(get_phone_service)]


def clear_service_caches() -> None:
    """Clear all cached service instances (for testing)."""
    get_llm_service.cache_clear()
    get_ticket_service.cache_clear()
    get_knowledge_service.cache_clear()
    get_session_store.cache_clear()
    get_audit_log.cache_clear()
    get_branding_service.cache_clear()
    get_realtime_service.cache_clear()
    get_phone_service.cache_clear()
