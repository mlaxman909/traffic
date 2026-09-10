# SignalAI: JWT Authentication Implementation

## Overview

The SignalAI project has transitioned from a mock authentication prototype to a fully secure, JWT-based authentication system using Argon2 for password hashing. This documentation outlines the design decisions, implementation details, and architecture of the newly secured API and frontend.

## 1. Backend Implementation (FastAPI)

### Dependencies
- **pwdlib[argon2]**: Used for secure password hashing.
- **PyJWT**: Used to encode and decode JSON Web Tokens.

### Endpoints
- **`POST /api/auth/login`**: Accepts `username` (email) and `password` as `application/x-www-form-urlencoded`. Validates credentials against the `users` table and issues a short-lived `access_token`.
- **`GET /api/auth/me`**: Returns the `User` object for the currently authenticated token.

### Security Implementation
- Created `backend/app/services/auth.py` containing `verify_password`, `get_password_hash`, and the `get_current_user` dependency.
- Passwords for the 6 demo users were migrated from static phase-1 placeholders to secure Argon2 hashes of `"password123"` using a one-time migration script.
- The `get_current_user` dependency has been applied to **ALL write operations (POST, PUT, DELETE)** across all routers: `users`, `junctions`, `traffic_records`, `signal_timings`, `ai_recommendations`, `emergency_routes`, and `operator_logs`.

### Authorization Logic
- `ai_recommendations`: When an operator approves/rejects an AI recommendation, the API now securely overrides the `reviewed_by` field with `current_user.id`.
- `emergency_routes`: When a new route is planned, `created_by` is securely mapped to `current_user.id`.
- `operator_logs`: All logs correctly reflect the acting user's ID via `current_user.id` when appending to the immutable audit trail.

## 2. Frontend Implementation (React)

### Auth Context
- **`AuthContext.jsx`**: Provides a global authentication state (`currentUser`, `token`, `isAuthenticated`, `login`, `logout`) via React Context.
- It parses tokens, securely stores them in `localStorage`, and handles re-hydration on application load via the `/api/auth/me` endpoint.

### Protected Routing
- **`ProtectedRoute.jsx`**: Validates `isAuthenticated`. If unauthenticated, gracefully intercepts navigation and redirects to `/login` (with `location.state.from` retention).
- Extends role-based protection (e.g. `allowedRoles={['SYSTEM_ADMINISTRATOR']}` used for Admin User and Admin Junction pages).

### Service API Integration
- `src/services/api.js` was refactored to intercept API calls globally and prepend the `Authorization: Bearer <token>` header to all requests.
- Automatic global logout on `401 Unauthorized`.

### UI Enhancements
- **Login Page**: Refactored to collect `Email Address` instead of generic `Operator ID`. Connected to real FastAPI authentication endpoint. Removed fake 1.2s timeout.
- **Sidebar / Header**: Now extracts the actual user name, role, and email from the `currentUser` object instead of static mock data.

## 3. Database Safety
All implementation was successfully executed without recreating the database or dropping any existing tables. The integrity of the 23,048 traffic records remains intact.
