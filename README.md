# Distributed Rate Limiting Service

A production-ready distributed rate limiting backend service built with **FastAPI** and **Redis**.  
Enforces API request quotas using a **sliding window algorithm** — stateless, horizontally scalable, and cloud-native.

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)
![Redis](https://img.shields.io/badge/Redis-7.x-red)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🎯 Problem Statement

In large-scale backend systems, APIs must be protected from abuse, accidental overuse, and denial-of-service scenarios.  
This service provides **centralized, distributed rate limiting** that can be shared across multiple API instances.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│    Redis    │
│  (API Key)  │     │  (Stateless)│     │ (State Store)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Lua Script │
                    │  (Atomic)   │
                    └─────────────┘
```

**Key Design Decisions:**
- **Sliding Window Algorithm** — Precise request counting, avoids fixed-window burst issues
- **Atomic Lua Scripts** — Race-condition-free Redis operations in a single round-trip
- **Stateless API** — Horizontally scalable, Redis handles all coordination

---

## 📁 Project Structure

```
├── app/
│   ├── main.py           # FastAPI app + rate limit middleware
│   ├── rate_limiter.py   # Sliding window implementation (Lua script)
│   └── analytics.py      # Request/violation logging
├── docker-compose.yml    # Local dev stack (API + Redis)
├── Dockerfile
├── requirements.txt
└── redis.conf
```

---

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/cyb3rcr4t0712/distributed-rate-limiter.git
cd distributed-rate-limiter
docker-compose up --build

# Health check
curl http://localhost:8000/health

# Test rate limiting (100 req/min limit)
for i in {1..110}; do \
  curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST -H "X-API-Key: test" \
  http://localhost:8000/api/resource; \
done
# First 100 return 200, then 429s kick in
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (bypasses rate limit) |
| `GET` | `/` | Root endpoint |
| `POST` | `/api/resource` | Protected resource |

**Headers Returned:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
```

**Rate Limited Response:**
```json
HTTP 429
{"detail": "Too many requests. Please retry later."}
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `DEFAULT_LIMIT` | `100` | Requests per window |
| `DEFAULT_WINDOW` | `60000` | Window size (ms) |

---

## ☁️ Cloud Deployment

Designed for deployment on **Google Cloud Run** with **Redis Cloud** (or GCP Memorystore).

```bash
# Build & push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT/rate-limiter-repo/rate-limiter:latest .

# Deploy to Cloud Run
gcloud run deploy rate-limiter-api \
  --image=us-central1-docker.pkg.dev/PROJECT/rate-limiter-repo/rate-limiter:latest \
  --set-env-vars="REDIS_URL=rediss://default:PASS@HOST:PORT" \
  --allow-unauthenticated
```

---

## 📈 Future Improvements

- [ ] Per-client configurable rate limits
- [ ] Prometheus metrics export
- [ ] Admin dashboard
- [ ] Global rate limiting across regions

---

## 📄 License

MIT License © 2026 Shreyash
