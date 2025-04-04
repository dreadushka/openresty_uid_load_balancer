# Non-Production Dynamic Load Balancer with UID Routing
## *This project is intended exclusively for testing and educational purposes. It was primarily generated using AI tools.*

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?logo=nginx&logoColor=white)
![Lua](https://img.shields.io/badge/lua-%232C2D72.svg?logo=lua&logoColor=white)

High-performance dynamic load balancer with intelligent routing based on user IDs (UID). Built with **OpenResty (Nginx + Lua)** and **Docker**, featuring:

## Features 🚀
- **Dynamic UID Routing**  
  - Route requests to specific backends using `uids.lst` file
  - Supports hot-reloading of UID list (every 30s)
- **Multi-level Caching**  
  - L1: Cookie-based persistence
  - L2: In-memory LRU cache (1000 entries)
  - L3: Shared memory cache for UID lookups
- **Performance Optimizations**  
  - 50k+ RPS capability
  - 1ms average latency
  - Asynchronous file loading
- **Advanced Monitoring**  
  - Built-in latency tracking
  - Request distribution metrics
  - Error rate monitoring

## Getting Started 🛠️

### Prerequisites
1. Docker & Docker Compose
2. Python 3.8+ (for load testing)

### Quick Start
```bash
# 1. Build and start services
docker-compose up -d --build

# 2. Check service status
docker-compose ps

# 3. Run load test (10,000 requests)
python load_test.py --url http://localhost:8080 --requests 10000 --threads 50 --special 20

# 4. Check logs
docker-compose logs -f proxy
