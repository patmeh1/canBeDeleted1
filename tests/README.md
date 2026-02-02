# Test Suite Summary

## Overview
Comprehensive test suite for the Mergington High School Activities API with **100% code coverage**.

## Test Statistics
- **Total Tests**: 55
- **Passed**: 55 (100%)
- **Code Coverage**: 100%

## Test Organization

### 1. Basic API Tests (`test_api_basics.py`) - 9 tests
Tests fundamental API functionality:
- Root endpoint redirects
- GET /activities endpoint
- Response formats and data structures
- Activity field validation
- Data type verification

### 2. Signup Tests (`test_signup.py`) - 17 tests

#### Success Cases (7 tests)
- New student signup
- Student added to participant list
- Success message returned
- Multiple students signup
- Same student in different activities
- URL-encoded activity names
- Special characters in emails

#### Error Cases (7 tests)
- Non-existent activity (404)
- Duplicate signup (400)
- Already registered participant (400)
- Empty activity name
- Proper error messages

#### Edge Cases (3 tests)
- Participant order preservation
- Activity isolation
- Case sensitivity

### 3. Unregister Tests (`test_unregister.py`) - 18 tests

#### Success Cases (7 tests)
- Existing student unregister
- Student removed from list
- Success message returned
- Multiple students unregister
- Unregister from multiple activities
- URL-encoded activity names
- Other participants unaffected

#### Error Cases (7 tests)
- Non-existent activity (404)
- Non-registered student (400)
- Unregister twice (400)
- Wrong activity (400)
- Empty activity name
- Proper error messages

#### Edge Cases (4 tests)
- Participant order preservation
- Activity isolation
- Case sensitivity (activity)
- Case sensitivity (email)

### 4. Integration Tests (`test_integration.py`) - 11 tests

#### Signup/Unregister Integration (3 tests)
- Complete signup/unregister cycle
- Re-signup after unregister
- Complex multi-student workflows

#### Capacity Management (3 tests)
- Max participant limits
- Fill to capacity
- Participant count accuracy

#### Data Integrity (4 tests)
- Structure consistency
- No duplicates
- Activity isolation
- Valid email formats

#### Concurrent Operations (2 tests)
- Multiple simultaneous signups
- Concurrent signup and unregister

## Coverage Details

### Endpoints Tested
- ✅ `GET /` (root redirect)
- ✅ `GET /activities` (list all activities)
- ✅ `POST /activities/{activity_name}/signup` (register participant)
- ✅ `DELETE /activities/{activity_name}/unregister` (remove participant)

### Test Categories
- ✅ **Happy Path**: Normal successful operations
- ✅ **Error Handling**: 404 and 400 error cases
- ✅ **Edge Cases**: Boundary conditions and special scenarios
- ✅ **Data Validation**: Field types and formats
- ✅ **State Management**: Data persistence and isolation
- ✅ **Integration**: Multi-step workflows

## Key Features Tested

### Functional Requirements
- [x] View all activities
- [x] Sign up for activities
- [x] Unregister from activities
- [x] Duplicate prevention
- [x] Activity capacity tracking
- [x] Participant list management

### Quality Assurance
- [x] HTTP status codes
- [x] JSON response formats
- [x] Error messages
- [x] Data consistency
- [x] Activity isolation
- [x] State preservation
- [x] URL encoding
- [x] Case sensitivity

### Edge Cases Covered
- [x] Empty strings
- [x] Special characters
- [x] URL encoding
- [x] Multiple operations
- [x] Order preservation
- [x] Capacity limits
- [x] Duplicate detection
- [x] Non-existent resources

## Running the Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_signup.py -v
```

### Run specific test class
```bash
pytest tests/test_signup.py::TestSignupSuccess -v
```

### Run specific test
```bash
pytest tests/test_signup.py::TestSignupSuccess::test_signup_new_student_returns_200 -v
```

## Dependencies
- `pytest` - Testing framework
- `httpx` - HTTP client for testing
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
