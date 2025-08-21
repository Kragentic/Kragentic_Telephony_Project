# Contact List Manager - Implementation Todo

## Task 11: Create Contact List Manager
**Status**: pending  
**Priority**: medium  
**Dependencies**: Task 3 (PostgreSQL Database)

## Overview
Build system for managing contact lists and campaigns with CSV import, validation, and scheduling capabilities.

## Implementation Checklist

### Phase 1: Database Schema & Models
- [ ] Create Contact schema with fields:
  - id (UUID)
  - phone (E.164 format)
  - name (string)
  - metadata (JSONB)
  - blacklisted (boolean)
  - inserted_at (timestamp)
  - updated_at (timestamp)
- [ ] Add database indexes:
  - [ ] Index on phone number
  - [ ] Index on blacklisted flag
  - [ ] Composite index on (phone, blacklisted)

### Phase 2: Context Module & CRUD Operations
- [ ] Create ContactManager context module
- [ ] Implement basic CRUD functions:
  - [ ] `list_contacts/0` - List all contacts
  - [ ] `get_contact!/1` - Get single contact
  - [ ] `create_contact/1` - Create new contact
  - [ ] `update_contact/2` - Update existing contact
  - [ ] `delete_contact/1` - Delete contact
  - [ ] `change_contact/1` - Generate changeset

### Phase 3: CSV Import System
- [ ] Create CSV import endpoint `/api/contacts/import`
- [ ] Implement CSV parsing with proper error handling
- [ ] Add schema validation:
  - [ ] Phone number format validation (E.164)
  - [ ] Name field sanitization
  - [ ] Metadata JSON validation
- [ ] Implement batch processing:
  - [ ] Process in chunks of 100 records
  - [ ] Track import progress
  - [ ] Generate import report

### Phase 4: Phone Number Validation
- [ ] Create phone validation module
- [ ] Implement E.164 format validation
- [ ] Add phone number normalization
- [ ] Handle international formats
- [ ] Validate against blacklist

### Phase 5: Background Job Processing
- [ ] Install Oban dependency
- [ ] Configure Oban for contact processing
- [ ] Create contact processing worker
- [ ] Implement retry logic:
  - [ ] Max 3 attempts
  - [ ] Exponential backoff
  - [ ] Dead letter queue for failures

### Phase 6: API Endpoints
- [ ] Create RESTful API endpoints:
  - [ ] `GET /api/contacts` - List contacts (paginated)
  - [ ] `GET /api/contacts/:id` - Get contact
  - [ ] `POST /api/contacts` - Create contact
  - [ ] `PUT /api/contacts/:id` - Update contact
  - [ ] `DELETE /api/contacts/:id` - Delete contact
  - [ ] `POST /api/contacts/import` - CSV import
  - [ ] `GET /api/contacts/blacklist` - Get blacklisted numbers

### Phase 7: Testing
- [ ] Create test data fixtures
- [ ] Write unit tests for:
  - [ ] Contact schema validation
  - [ ] Phone number validation
  - [ ] CSV import functionality
  - [ ] API endpoints
- [ ] Write integration tests:
  - [ ] Full CSV import flow
  - [ ] Error handling scenarios
  - [ ] Concurrent import handling

### Phase 8: Documentation
- [ ] Create API documentation
- [ ] Add usage examples
- [ ] Document CSV format requirements
- [ ] Create troubleshooting guide

## CSV Format Specification
```csv
phone,name,metadata
"+1234567890","John Doe","{\"custom_field\": \"value\"}"
"+1987654321","Jane Smith","{\"notes\": \"VIP customer\"}"
```

## Validation Rules
- Phone: Must be in E.164 format (+1234567890)
- Name: Required, max 255 characters
- Metadata: Valid JSON object (optional)

## Error Handling
- Invalid phone format → Skip record, log error
- Duplicate phone → Update existing contact
- Invalid JSON → Skip metadata field
- Network errors → Retry with exponential backoff

## Performance Considerations
- Batch insert for large CSV files
- Database indexes for fast lookups
- Background processing for large imports
- Rate limiting on API endpoints
