# Database Scaling — How to Scale to Millions of Users

**Source:** [Instagram Reel — Scaling Lab](https://www.instagram.com/reel/Dc9vMsSMiIy/)
**Added:** 2026-09-12
**Tags:** database, scaling, postgres, redis, architecture, engineering

## The Progression (do this in order, not all at once)

1. **Vertical scaling** — more CPU/RAM/disk on the single DB. Gets you further than people think.
2. **Indexes** — stop doing full table scans. Filter by email constantly? Index email. O(log n) vs O(n).
3. **Caching (Redis)** — hot data read 100k times/day shouldn't hit DB 100k times. Most reads never touch DB.
4. **Read replicas** — primary handles writes, replicas handle reads. Distribute read traffic.
5. **Async queues** — analytics, notifications, recommendations don't block the response. Fire-and-forget.
6. **Partitioning** — billions of rows? Split by date/region/customer. Queries only scan the partition they need.
7. **Polyglot persistence** — stop asking one DB to do everything:
   - Postgres → user accounts
   - Redis → sessions, caching
   - Elasticsearch → search
   - S3 → files
   - Columnar DB → analytics
8. **Sharding** — LAST RESORT. Split data across multiple DBs. Serious complexity (hot shards, cross-shard queries). Only when writes are truly the bottleneck.

## The Money Quote
> "The biggest mistake is starting with distributed architecture because you think you might have millions of users someday. Complexity is expensive. Scale when the bottleneck actually appears."

## CEV Stack Status
- Supabase (Postgres) + Redis already in place ✅
- Next lever if needed: read replicas (Supabase supports this natively)
- Then: Redis caching for hot creator profiles
- Then: partition creator DB by region or platform
- Sharding: years away if ever
