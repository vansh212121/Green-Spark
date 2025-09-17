⚡ GreenSpark – Smart Energy Management Platform

GreenSpark is a full-stack, AI-powered platform for energy management.
It ingests user electricity bills, parses them with AI (Google Gemini), estimates appliance-level consumption, and generates actionable insights for smarter energy use.

This project combines a robust FastAPI backend (with Celery, PostgreSQL, Redis, MinIO) and a modern React frontend (with Redux Toolkit, TailwindCSS, Recharts).

🌟 Features

🔐 Secure Authentication → JWT auth, refresh token rotation, Redis blacklist, Argon2 password hashing.

📂 Smart Bill Processing → Presigned S3 uploads, AI-based parsing, structured JSON validation.

⚡ Appliance Estimation → Algorithmic breakdown of energy consumption.

📊 AI Insights → Automated reports with energy-saving recommendations.

🧩 Scalable Architecture → Dockerized, multi-container deployment.

🚦 Rate Limiting & Caching → Redis-powered request throttling + performance caching.

🎨 Modern Frontend → Responsive UI with charts, graphs, and real-time updates.

🛠️ Tech Stack
Backend

Framework: FastAPI (async-first)

ORM: SQLModel (Pydantic + SQLAlchemy)

DB: PostgreSQL (with Alembic migrations)

Async Tasks: Celery + Redis

File Storage: MinIO (S3-compatible)

AI: Google Gemini API

Security: JWT (python-jose), Argon2 (passlib), RBAC, rate limiting

Containerization: Docker & Docker Compose

Dependency Management: Poetry

Frontend

Framework: React 18 + Vite

State: Redux Toolkit + RTK Query

UI: TailwindCSS, shadcn/ui, lucide-react

Routing: React Router DOM

Charts: Recharts

Notifications: Sonner

📐 Backend Architecture & Features
🧱 Layered Design

Routers (API Layer) → Handles requests, dependencies, and response validation.

Services (Business Layer) → Encapsulates domain logic, coordinates repositories & tasks.

Repositories (Data Layer) → Clean CRUD abstraction on top of SQLModel.

## ⚙️ Dependency Injection

The backend makes extensive use of **FastAPI’s `Depends()` pattern** to keep business logic clean, reusable, and testable.

### 🔐 Authentication & User Context

- `get_current_user` – validates JWT access tokens and attaches the current user to the request.
- `get_current_active_user` – ensures the user is active.
- `get_current_verified_user` – ensures the user’s email is verified.
- `get_current_user_optional` – allows endpoints to gracefully handle both authenticated and anonymous users.

**Features:**

- JWT validation with revocation checks.
- Automatic brute-force protection with **rate-limited authentication attempts**.
- User context (`request.state.user`, `request.state.user_id`) available for logging and auditing.

### 👮 Role-Based Access Control (RBAC)

- `RoleChecker` dependency enforces role hierarchy (`USER`, `ADMIN`).
- Prevents privilege escalation by comparing role priorities.
- Preconfigured dependencies:

  - `require_user` – requires at least `USER`.
  - `require_admin` – requires `ADMIN`.

### 🚦 Rate Limiting

- `RateLimitChecker` dependency enforces request quotas per IP or per user.
- Preconfigured limits:

  - **Auth attempts** → 5/min (IP-based).
  - **General API calls** → 35/min (per user).
  - **Heavy endpoints** → 10/min (per user).
  - **Refresh tokens** → 3/day (per user).

### 🔎 Pagination, Search & Filtering

- `PaginationParams` and `get_pagination_params` provide:

  - `page`, `size`, `skip`, `limit` values.
  - Enforced **maximum page size** (configurable via settings).

- Consistent pagination across bills, appliances, and insights endpoints.
- Flexible query support for search and filtering.

### ⚡ Performance & Caching

- **Redis-backed services** injected via dependencies:

  - Token blacklist (secure logout/session invalidation).
  - Request caching for frequently accessed queries.
  - Distributed **rate limiting** (per IP or per user).

### 🛠️ Utility Dependencies

- `get_request_context` – extracts `client_ip`, `user_agent`, `path`, `method`, `request_id`, and `user_id`.
- `get_health_status` – provides health check metadata (status, timestamp, version).

---

## 🛡️ Security

The backend includes a **comprehensive security framework** covering authentication, authorization, password management, token lifecycle, and secure headers.

### 🔑 Authentication & Tokens

- **JWT-based Authentication** with **access** and **refresh tokens**.
- Token lifecycle fully managed by `TokenManager`.
- Supports multiple token types:

  - `ACCESS` – short-lived tokens for API calls.
  - `REFRESH` – long-lived tokens to issue new access tokens.
  - `EMAIL_VERIFICATION`, `PASSWORD_RESET`, `EMAIL_CHANGE`.

- **Refresh Token Rotation**: old refresh tokens are revoked immediately after use.
- **Blacklist / Revocation** (via Redis):

  - Each JWT has a unique `jti` claim.
  - Tokens can be revoked individually or in bulk.
  - Fail-secure mode: if Redis is unavailable, token checks fail securely.

- **Leeway Handling**: Configurable clock skew tolerance (`JWT_LEEWAY_SECONDS`).

### 🔒 Password Management

- Secure password hashing with **Argon2 (preferred)**, fallback to bcrypt.
- Automatic rehashing if parameters become outdated (`needs_rehash`).
- Transparent upgrades: verified passwords can be rehashed with stronger params without user disruption.
- Constant-time comparison to mitigate timing attacks.

### 👮 Authorization

- **Role-Based Access Control (RBAC)** with a `RoleChecker` dependency.
- Ensures only users with appropriate roles/permissions can access protected endpoints.

### 🚫 Token Revocation

- Tokens can be invalidated by:

  - Explicit revocation (`revoke_token`).
  - Revocation by `jti` when claims already parsed.

- TTL (time-to-live) is automatically calculated from the token’s expiry.
- Redis ensures **real-time token invalidation** across distributed systems.

### 📜 Security Headers

All API responses include recommended **security headers** via `SecurityHeaders`:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### 🛡️ Example Secure Practices

- **Access Token TTL**: 15 minutes (configurable).
- **Refresh Token TTL**: 7 days (configurable).
- **Issuer & Audience Validation**: prevents token misuse across apps.
- **Secure Random Generators**: `generate_secure_token()` uses `secrets` for CSRF/email tokens.

---

✅ Together, these measures provide **defense in depth** against common attack vectors: credential stuffing, replay attacks, token theft, timing attacks, and misconfigured clients.

---

🧵 Async Tasks (Celery)

Email processing tasks(Welcome, verfication, password-reset, email-change).

Bill processing pipeline:

Parse bill with Gemini.

Estimate appliances.

Generate insights with Gemini.

Tasks run asynchronously in worker containers.

## 🛡️ Middleware

The backend includes a robust middleware stack to ensure **security, performance, and maintainability**. The order of middleware execution is critical, and the project follows a carefully chosen strategy:

### Correct Middleware Order Strategy

1. **Logging & Error Handling**

   - Outermost middleware to catch _all_ requests and errors.
   - Ensures centralized logging and custom exception responses.

2. **CORS (Cross-Origin Resource Sharing)**

   - Runs early to properly handle `OPTIONS` preflight requests.
   - Adds required CORS headers before other middleware.

3. **Trusted Host**

   - Validates the `Host` header against a whitelist.
   - Helps prevent [Host Header Attacks](https://portswigger.net/web-security/host-header).

4. **Security Headers**

   - Adds secure headers (`X-Frame-Options`, `Content-Security-Policy`, etc.).
   - Enhances app protection against common attacks.

5. **GZip Compression**

   - Compresses large responses for performance.
   - Runs _after_ security headers to avoid conflicts.

6. **Request Size Limiter**

   - Innermost middleware to reject overly large request bodies early.
   - Protects the server from DoS attacks and resource abuse.

### Custom Middleware Highlights

- **Custom Exception Handler**: Centralized error format for all API responses.
- **Structured Logging**: Captures request/response cycle with correlation IDs.
- **Security Layer**: Extra checks on headers, body size, and access patterns.

---

⚡ This structure ensures:

- Errors are always logged and surfaced in a consistent format.
- Security checks and headers are enforced early.
- Heavy payloads are rejected before reaching business logic.
- Performance is maximized with GZip and caching.

## 🚨 Exception Handling

The backend includes a **centralized, layered exception handling system** designed for consistency, security, and debuggability.

### 📂 Exception Architecture

- **`exceptions.py`**

  - Defines a structured hierarchy of custom exceptions.
  - All exceptions inherit from a single base: `AppException`.
  - Uses an `ErrorCode` enum to standardize error identifiers across the codebase.
  - Provides `to_dict()` to serialize errors into a consistent JSON format.

- **`exception_utils.py`**

  - Provides helper utilities for raising and handling exceptions.
  - `handle_exceptions`: Decorator that wraps functions (sync or async) and converts unknown errors into structured `AppException`s.
  - `raise_for_status`: Utility to raise exceptions conditionally (e.g., `raise_for_status(user is None, ResourceNotFound, resource_id=id)`).

- **`exception_handler.py`**

  - Central registry for FastAPI exception handlers.
  - Converts framework-level and unhandled exceptions into **uniform JSON responses**.
  - Includes structured logging for observability.

### 🛠️ Exception Flow

1. **Custom Exceptions (`AppException`)**

   - Application-specific errors such as authentication, authorization, and resource not found.
   - Example: `InvalidCredentials` returns `401 Unauthorized` with error code `INVALID_CREDENTIALS`.

2. **Validation Exceptions**

   - Catches FastAPI/Pydantic validation errors.
   - Normalizes them into a JSON format with `field`, `message`, `type`, and optional `context`.

3. **HTTP Exceptions**

   - Converts Starlette’s native `HTTPException` into the same structured JSON format.

4. **Unhandled Exceptions**

   - Captures any unexpected errors.
   - Generates a unique `error_id` (UUID) for tracking in logs and client responses.
   - Prevents internal stack traces from leaking to clients.

### 📊 Example Error Response

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect email or password",
    "status_code": 401,
    "context": {}
  }
}
```

### ✅ Benefits

- **Consistency**: All errors follow the same JSON format.
- **Debuggability**: Errors are logged with rich context (status, method, path, error_id).
- **Safety**: Internal errors never leak sensitive details.
- **Flexibility**: New exceptions can be added by subclassing `AppException`.

🗄️ Database & Alembic

Models built with SQLModel.
Schemas built with Pydantic for Validation.

Alembic handles migrations:

poetry run alembic revision --autogenerate -m "your message"
poetry run alembic upgrade head

Developers must push their own migrations when models changes occur.

🖥️ Frontend Architecture & Features
🔑 Auth & Session

JWT-based with auto-refresh via RTK Query middleware.

Session persistence with localStorage + Redux.

Secure logout clears Redux state + Redis blacklist.

🧩 State & API Layer

Redux Toolkit slices: authSlice, uiSlice.

RTK Query slices: authApi, userApi, billApi, applianceApi, insightApi.

Automatic caching, refetching, and error handling.

📊 Data-Driven UI

Bills Page → Upload & manage bills (with status updates).

Appliances Page → CRUD appliances per bill + quick stats.

Insights Page → Long-running tasks with polling.

Overview Dashboard → Charts powered by derived frontend logic.

🎨 Visualization

Recharts for pie, bar, scatter charts.

Legend wrapping + custom layouts for readability.

Skeleton loaders for seamless UX.

🏗️ Running Locally
1️⃣ Clone Repository
git clone https://github.com/vansh212121/Green-Spark.git
cd greenspark

2️⃣ Backend Setup
cd backend

# Install dependencies

poetry install

# Set environment variables (example: .env file)

cp .env.example .env

# Run migrations

poetry run alembic upgrade head

# Start services

docker-compose up -d

Backend will be available at http://127.0.0.1:8000/api/v1

3️⃣ Frontend Setup
cd frontend

# Install dependencies

npm install

# Start dev server

npm run dev

Frontend will be available at http://127.0.0.1:5173

✅ Final Checklist for Contributors

Run poetry install before starting backend.

Apply database migrations manually via Alembic.

Ensure Docker services (postgres, redis, minio) are running.

Configure .env files for both frontend & backend.

📌 Status

✅ Backend: Complete with DI, caching, rate-limiting, exception handling, async pipeline.

✅ Frontend: Complete with protected routes, Redux, charts, polling, error handling.

✅ Deployment: Ready for Dockerized deployment.

📄 License

MIT License – Free to use and modify.
