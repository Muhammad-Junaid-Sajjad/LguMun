# Feature Specification: LGU MUN 2026 Delegate Registration

**Feature Branch**: `001-delegate-registration`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: LGU MUN 2026 Phase 0 delegate registration system with auto roll number assignment, 9 committees, Hogwarts theme

## User Scenarios & Testing

### User Story 1 - Successful Delegate Registration (Priority: P1)

A delegate visits the registration page, fills in their details (name, student ID, email, phone, institution), selects a committee, and receives a unique roll number on the success screen.

**Why this priority**: Core feature - without this, the system has no value. All other features depend on successful registration working.

**Independent Test**: Can be fully tested by completing a registration form end-to-end and verifying roll number is generated and displayed.

**Acceptance Scenarios**:

1. **Given** delegate is on registration page, **When** they fill all required fields with valid data and select an available committee, **Then** they receive a unique roll number (format: LGU-MUN26-XXX) on success screen
2. **Given** delegate completes registration, **When** success page loads, **Then** roll number is displayed prominently in gold, along with name, committee, and email confirmation
3. **Given** delegate is on success screen, **When** they view the page, **Then** they see a "Save this number" message and can navigate back to homepage or committees page

---

### User Story 2 - Duplicate Prevention (Priority: P1)

When a delegate attempts to register with an email or student ID that already exists, the system blocks the registration and shows a clear error message on the correct field.

**Why this priority**: Critical for data integrity - prevents duplicate registrations and maintains one-to-one mapping between delegates and roll numbers.

**Independent Test**: Can be fully tested by attempting duplicate registration with same email/ID and verifying error is shown and no new record is created.

**Acceptance Scenarios**:

1. **Given** a delegate with email "john@example.com" is already registered, **When** another delegate tries to register with the same email, **Then** error "DUPLICATE_EMAIL" is shown on the email field and no new record is created
2. **Given** a delegate with student ID "12345" is already registered, **When** another delegate tries to register with the same ID, **Then** error "DUPLICATE_ID" is shown on the student ID field
3. **Given** email is submitted in uppercase "JOHN@EXAMPLE.COM", **When** system checks for duplicates, **Then** it matches against lowercase stored email and blocks registration if duplicate exists

---

### User Story 3 - Committee Capacity Management (Priority: P1)

When a committee reaches full capacity, the system prevents new registrations for that committee. The dropdown shows full committees as disabled, and direct API attempts are blocked server-side.

**Why this priority**: Prevents overbooking and ensures fair distribution across committees. Race condition handling is critical for last-seat scenarios.

**Independent Test**: Can be fully tested by filling a committee to capacity and verifying no more registrations are accepted for that committee.

**Acceptance Scenarios**:

1. **Given** a committee has 30 total seats and 30 delegates registered, **When** a new delegate tries to register for that committee, **Then** they receive error "COMMITTEE_FULL" and registration is rejected
2. **Given** a committee is at capacity, **When** delegate views the registration form, **Then** that committee appears disabled in the dropdown with "(FULL)" label
3. **Given** two delegates submit simultaneously for the last available seat, **When** both requests reach the server, **Then** exactly one succeeds with a roll number and the other receives "COMMITTEE_FULL" error

---

### User Story 4 - Committee Browsing (Priority: P2)

A delegate can view all 9 committees with their details (name, chair, agenda, available seats, language) before deciding to register. The committees page shows live seat availability and progress bars.

**Why this priority**: Enables informed decision-making. Delegates need to see all options before committing to a committee.

**Independent Test**: Can be fully tested by loading committees page and verifying all 9 committees are displayed with correct information and live seat counts.

**Acceptance Scenarios**:

1. **Given** delegate visits committees page, **When** page loads, **Then** all 9 committees are displayed with name, chair name, agenda, total seats, filled seats, and language
2. **Given** committees page is loaded, **When** delegate views a committee, **Then** they see a progress bar showing capacity percentage and a "FULL" badge if at capacity
3. **Given** PNA committee is displayed, **When** delegate views it, **Then** language is shown as "Urdu & English" (different from other committees which show "English")

---

### User Story 5 - Input Validation (Priority: P1)

The system validates all user input both client-side (for UX) and server-side (for security). Invalid data is rejected with clear error messages showing which fields have errors.

**Why this priority**: Prevents invalid data from entering the database and ensures security. Server-side validation is non-negotiable.

**Independent Test**: Can be fully tested by submitting invalid data (empty fields, bad email, bad phone) and verifying all errors are shown at once.

**Acceptance Scenarios**:

1. **Given** delegate submits form with empty required fields, **When** form is validated, **Then** all empty fields show error messages simultaneously
2. **Given** delegate enters invalid email format, **When** server validates, **Then** error "Invalid email format" is shown on email field
3. **Given** delegate enters phone number with invalid format, **When** server validates, **Then** error "Invalid phone number" is shown and phone is stripped of non-numeric characters before validation
4. **Given** delegate submits form with special characters in name (e.g., "O'Brien", Arabic characters), **When** server validates, **Then** name is accepted as-is (UTF-8 support)

---

### User Story 6 - Rate Limiting (Priority: P2)

The system protects against spam by limiting registration attempts to 5 requests per 10 minutes per IP address. Exceeding this limit returns HTTP 429.

**Why this priority**: Prevents abuse and ensures fair access for legitimate users. Protects against automated spam attacks.

**Independent Test**: Can be fully tested by making 6 requests from same IP within 10 minutes and verifying 6th request returns HTTP 429.

**Acceptance Scenarios**:

1. **Given** a delegate makes 5 registration requests from IP 192.168.1.1 within 10 minutes, **When** they make a 6th request, **Then** they receive HTTP 429 (Too Many Requests)
2. **Given** rate limit is exceeded for one IP, **When** another IP makes requests, **Then** they are not affected and can register normally
3. **Given** 10 minutes have passed since the first request, **When** delegate makes a new request, **Then** the rate limit counter resets and they can make 5 new requests

---

### User Story 7 - Homepage & Navigation (Priority: P2)

The homepage displays event information, CTA buttons to register or browse committees, a photo gallery of past events, and preview cards for 3 featured committees. All pages have consistent navigation with the LGU MUN logo.

**Why this priority**: Creates professional first impression and guides users to key actions. Establishes brand identity with Hogwarts theme.

**Independent Test**: Can be fully tested by loading homepage and verifying all elements are present and navigation works across all 4 pages.

**Acceptance Scenarios**:

1. **Given** user visits homepage, **When** page loads, **Then** they see LGU MUN logo, event name/date/venue, 2 CTA buttons (Register, Browse Committees), photo gallery, and 3 committee preview cards
2. **Given** user is on any page, **When** they click the logo in navbar, **Then** they are taken to homepage
3. **Given** user is on any page, **When** they view the navbar, **Then** it displays consistently with logo at 48px height and Hogwarts theme styling

---

### Edge Cases

- **Email in uppercase**: System lowercases before storage and duplicate check
- **Phone with formatting**: System strips dashes/spaces (e.g., "0300-123-4567" → "03001234567") before validation
- **Committee not found**: If committee_id doesn't exist or is inactive, return COMMITTEE_NOT_FOUND error
- **Zero seat committee**: Committee with total_seats = 0 is always FULL and never selectable
- **Database failure mid-registration**: Transaction rolls back, user sees SERVER_ERROR 500, error is logged internally
- **Success page without URL params**: Show error "Please register again" and link back to registration
- **Roll number sequence exceeds 999**: Naturally extends to LGU-MUN26-1000 (no truncation)
- **Concurrent requests for same email**: Only first succeeds, others get DUPLICATE_EMAIL

## Requirements

### Functional Requirements

- **FR-01**: System MUST display homepage with logo, event name/date/venue, 2 CTA buttons, photo gallery, 3 committee preview cards, and footer
- **FR-02**: System MUST provide registration form with fields: Full Name, Student ID/CNIC, Email, Phone, Institution, Committee dropdown
- **FR-03**: System MUST validate all input client-side (required, email format, Pakistani phone regex) for UX feedback
- **FR-04**: System MUST validate all input server-side independently using Pydantic, regardless of client validation
- **FR-05**: System MUST block duplicate email registrations (case-insensitive comparison)
- **FR-06**: System MUST block duplicate Student ID/CNIC registrations
- **FR-07**: System MUST prevent registration for committees at capacity (server-enforced)
- **FR-08**: System MUST use SELECT FOR UPDATE + atomic transaction on every registration to prevent race conditions
- **FR-09**: System MUST generate sequential roll numbers in format LGU-MUN26-XXX (zero-padded) server-side
- **FR-10**: System MUST display success screen with roll number (large, gold), name, committee, email, save message, and 2 navigation buttons
- **FR-11**: System MUST provide committees page showing all 9 active committees with live data, progress bars, FULL badges, and language labels
- **FR-12**: System MUST disable full committees in dropdown (visible but unselectable)
- **FR-13**: System MUST enforce rate limiting: 5 requests / 10 min / IP → HTTP 429
- **FR-14**: System MUST include security headers on every response (X-Content-Type-Options, X-Frame-Options, etc.)
- **FR-15**: System MUST display LGU MUN logo in navbar on all 4 pages (48px height, object-fit: contain)
- **FR-16**: System MUST display past event photos in homepage gallery from frontend/assets/
- **FR-17**: System MUST apply Hogwarts theme throughout all pages (colors, fonts, styling)
- **FR-18**: System MUST render correctly on mobile (375px), tablet (768px), and desktop (1280px) viewports
- **FR-19**: System MUST include seed script that idempotently inserts 9 committees into database
- **FR-20**: System MUST provide health check endpoint GET /api/v1/health that returns 200 OK

### API Requirements

- **FR-21**: POST /api/v1/delegates MUST accept (full_name, student_id_cnic, email, phone, institution, committee_id) and return (roll_number, full_name, email, committee_name, committee_short_name) on success (201)
- **FR-22**: GET /api/v1/committees MUST return all active committees with computed is_full boolean and capacity_percentage integer
- **FR-23**: GET /api/v1/committees/{id} MUST return single committee or 404 if not found
- **FR-24**: Every API response MUST follow envelope format: {success, data/error, timestamp}
- **FR-25**: Every error response MUST include error code, message, and optional field name

### Key Entities

- **Committee**: Represents a UN committee or assembly. Attributes: id, short_name (UNGA, UNSC, etc.), full_name, chair_name, agenda_1, agenda_2, total_seats, filled_seats, language, is_active, created_at. Relationships: one-to-many with Delegate.
- **Delegate**: Represents a registered participant. Attributes: id, roll_number (unique), full_name, student_id_cnic (unique), email (unique, lowercase), phone, institution, committee_id (FK), created_at, ip_address (audit only). Relationships: many-to-one with Committee.

## Success Criteria

### Measurable Outcomes

- **SC-01**: Delegate can complete registration from homepage to success screen in under 2 minutes
- **SC-02**: Zero duplicate roll numbers exist in database after 100 concurrent registrations
- **SC-03**: Race condition test passes: 2 concurrent requests for last seat = 1 success + 1 COMMITTEE_FULL error
- **SC-04**: All 9 committees are visible and correctly displayed on committees page
- **SC-05**: System renders correctly on 375px mobile viewport without horizontal scroll
- **SC-06**: All pytest tests pass (100% green) with coverage > 80%
- **SC-07**: Security headers present on live URL (verified via curl -I)
- **SC-08**: LGU MUN logo displays correctly on all 4 pages without distortion (object-fit: contain)
- **SC-09**: Rate limiting works: 6th request from same IP within 10 min returns HTTP 429
- **SC-10**: Duplicate email/ID prevention works: second registration with same email/ID is rejected

## Constraints

- Roll numbers are permanent and never reused
- Chair names and agendas are updated directly in Supabase dashboard (no UI needed in Phase 0)
- Success screen data is passed via URL parameters only (no GET by roll number endpoint)
- No email confirmation required (success screen is the only confirmation)
- Zero npm packages in frontend (vanilla HTML/CSS/JS only)

## Assumptions

- Pakistani phone numbers follow format: 0300-XXXXXXX or 03001234567 (11 digits starting with 03)
- Email validation uses standard RFC 5322 format
- All timestamps are in UTC (ISO 8601 format)
- Supabase PostgreSQL free tier is sufficient for Phase 0 (no scaling concerns)
- Render.com free tier auto-deploys on every GitHub push
- LGU MUN logo and past event photos are provided in frontend/assets/
- Hogwarts theme colors/fonts are defined in CSS (no design system needed)
- 9 committees are fixed for Phase 0 (no dynamic committee creation)

## Out of Scope

- User login or authentication
- Admin panel or dashboard
- Email sending (confirmations, reminders, etc.)
- Payment processing
- File uploads (resumes, photos, etc.)
- Country or position assignments
- Delegate editing or cancellation
- PDF reports or exports
