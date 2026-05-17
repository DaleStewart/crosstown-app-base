# Hands-On Lab: Institutional Branding & Admin Features

**Lab Date**: 2026-01-22
**Prerequisites**: Completed base Front Door Support Agent implementation

This document contains specifications for features to be added during the hands-on customization lab.

---

## Lab Overview

In this lab, participants will extend the Front Door Support Agent with institutional branding capabilities and admin ticket management features. These features enable CIOs to see their institution reflected in the product during demos.

---

## User Story 6 - Configure Institutional Branding (Priority: P6)

An administrator (CIO or IT staff) wants to customize the support portal with their institution's branding to provide a cohesive, professional experience for students.

**Why this priority**: Institutional branding is essential for CIO demos and pilot deployments. Universities need to see themselves in the product before committing to adoption.

**Independent Test**: Can be tested by navigating to Admin > Branding, changing the primary color and institution name, and verifying the changes appear in the header and throughout the UI.

**Acceptance Scenarios**:

1. **Given** an admin navigates to the Branding settings panel, **When** they enter a logo URL, **Then** the logo appears in the header replacing the default icon.
2. **Given** an admin selects a new primary color using the color picker, **When** they save, **Then** all buttons, links, and accent colors update to use the new color.
3. **Given** an admin changes the institution name and tagline, **When** they save, **Then** the header displays the new institution name and tagline.
4. **Given** an admin wants to undo branding changes, **When** they click "Reset to Defaults", **Then** the branding reverts to the default University Support configuration.
5. **Given** an admin makes changes in the branding panel, **When** viewing the live preview section, **Then** they can see how the header will appear before saving.

---

## User Story 7 - Manage Tickets as Administrator (Priority: P7)

An administrator needs to triage, update, and manage support tickets across all departments from a central dashboard.

**Why this priority**: Admins need visibility into all tickets for triage, escalation handling, and operational oversight.

**Independent Test**: Can be tested by navigating to Admin > Tickets, viewing the ticket list, filtering by status/department, and updating a ticket's status.

**Acceptance Scenarios**:

1. **Given** an admin navigates to the Admin dashboard, **When** they view the Tickets tab, **Then** they see all tickets across all departments.
2. **Given** an admin wants to find escalated tickets, **When** they filter by status "escalated", **Then** only escalated tickets are displayed.
3. **Given** an admin selects a ticket, **When** they change the status to "in_progress" and assign it, **Then** the ticket is updated and the changes persist.
4. **Given** an admin resolves a ticket, **When** they add a resolution summary and close it, **Then** the resolution is recorded.

---

## Functional Requirements

### Institutional Branding (Admin)

- **FR-033**: System MUST allow administrators to configure institution logo via URL
- **FR-034**: System MUST allow administrators to configure primary brand color (hex format, e.g., #2563eb)
- **FR-035**: System MUST allow administrators to configure institution name displayed in header (max 200 characters)
- **FR-036**: System MUST allow administrators to configure tagline text (max 500 characters)
- **FR-037**: System MUST apply branding colors dynamically across UI elements (buttons, links, accents, active states)
- **FR-038**: System MUST persist branding configuration via API and localStorage for instant rendering
- **FR-039**: System MUST provide live preview of branding changes in admin panel before saving
- **FR-040**: System MUST provide option to reset branding to system defaults

### Admin Ticket Management

- **FR-041**: System MUST provide admin dashboard for viewing all tickets across departments
- **FR-042**: System MUST allow admins to filter tickets by status (open, in_progress, pending_info, escalated, resolved, closed)
- **FR-043**: System MUST allow admins to filter tickets by department
- **FR-044**: System MUST allow admins to update ticket status
- **FR-045**: System MUST allow admins to assign tickets to agents
- **FR-046**: System MUST allow admins to add resolution summaries when closing tickets
- **FR-047**: System MUST allow admins to delete tickets

---

## Key Entity

- **BrandingConfig**: Represents institution branding settings including logo_url (optional), primary_color (hex), institution_name, tagline, and updated_at timestamp

---

## Design Decisions (Session 2026-01-21)

- Q: How should institutions customize the UI for CIO demos? → A: Admin dashboard with branding settings panel for logo, colors, institution name, and tagline
- Q: What branding elements should be configurable? → A: Logo (via URL), primary color (hex), institution name (max 200 chars), tagline (max 500 chars)
- Q: How should branding be persisted? → A: API endpoint with in-memory storage (mock) + localStorage for instant rendering on page load
- Q: Should branding colors cascade through the UI? → A: Yes, dynamic CSS variables update Tailwind primary color classes at runtime
- Q: What ticket statuses should the system support? → A: open, in_progress, pending_info, escalated, resolved, closed

---

## Implementation Checklist

### Backend

- [ ] Add `BrandingConfig`, `BrandingUpdateRequest`, `BrandingResponse` schemas to `models/schemas.py`
- [ ] Add `BrandingServiceInterface` to `services/interfaces.py`
- [ ] Create `MockBrandingService` in `services/mock/branding_service.py`
- [ ] Add `get_branding_service()` dependency to `core/dependencies.py`
- [ ] Add `GET /api/admin/branding` endpoint to `api/routes.py`
- [ ] Add `PUT /api/admin/branding` endpoint to `api/routes.py`

### Frontend

- [ ] Add `BrandingConfig` interface to `types/index.ts`
- [ ] Add `getBranding()`, `updateBranding()` to `api/client.ts`
- [ ] Create `BrandingContext.tsx` in `context/`
- [ ] Wrap app with `BrandingProvider` in `main.tsx`
- [ ] Update `Header.tsx` to use dynamic branding
- [ ] Create `BrandingSettingsPanel.tsx` component
- [ ] Add "Branding" tab to `AdminDashboard.tsx`
- [ ] Add CSS variable support in `index.css`

---

## Verification Steps

1. **Backend API**
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --port 8000

   # Test endpoints:
   curl http://localhost:8000/api/admin/branding
   curl -X PUT http://localhost:8000/api/admin/branding \
     -H "Content-Type: application/json" \
     -d '{"logo_url":"https://example.edu/logo.png","primary_color":"#1E4D8C","institution_name":"Contoso University","tagline":"Excellence in Education"}'
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm run dev
   # Open http://localhost:5173
   # Navigate to Admin tab
   # Change branding settings
   # Verify header updates with new logo/name
   # Verify primary color changes throughout UI
   ```

3. **Persistence**
   - Change branding, refresh page → settings should persist (localStorage + API)
   - Clear localStorage, refresh → should load from API defaults
