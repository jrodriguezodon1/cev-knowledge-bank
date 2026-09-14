# TikTok Mobile API Scraping — SeekSocial / DataShack Method

> **Source:** https://tiktok-api.seeksocial.io  
> **Author:** DataShack (Reddit) / kuben-developer (HuggingFace)  
> **Dataset:** https://huggingface.co/datasets/kuben-developer/tiktok-videos-4b  
> **Last measured:** September 2026 (measurements re-run)  
> **Stack:** Go 1.24  
> **Summary:** Scraped 5.94 billion TikTok videos, 3.23 billion creator profiles, and 2.8 billion comments in three weeks using TikTok's private Android app API — no login, no accounts.

---

## Background & Context

Almost every TikTok scraper in the wild either drives a headless browser or hits the public web endpoints. Both are the wrong layer — slow, fragile, and missing most of the interesting fields. The Android app (`com.zhiliaoapp.musically`) talks to a **private HTTP+JSON API** that is faster, more stable, and returns considerably more data.

The developer (DataShack) reverse-engineered this API over roughly two years, published a comprehensive write-up, a free 4.5 billion-row dataset on HuggingFace, and sells the full codebase.

---

## 1. Technical Method

### 1.1 The Four Gates (all must be correct or you get silent HTTP 200 empty body)

The most critical insight: **TikTok's soft block is not an error code — it's a clean `HTTP 200` with zero bytes in the body.** Your HTTP client reports success, logs stay green, and the database fills with empty rows. Four completely unrelated failures all produce the same symptom:

1. **Device was never activated** (§ activation)
2. **Signature is wrong** (§ X-Argus)
3. **Wrong regional host** (§ regions)
4. **TLS handshake fingerprint looks like a server, not a phone** (§ JA3)

There is no signal telling you which gate failed. You must fix all four and test each in isolation.

---

### 1.2 Device Registration & Identity

**Endpoint:** `/service/2/device_register/` on TikTok's logging host

TikTok **issues** `device_id` and `iid` — you cannot invent them. You submit a plausible Android device profile and receive back a real credential pair.

**Key identity fields:**

| Field | What it is | Origin |
|---|---|---|
| `aid` | App ID: `1233` = main TikTok, `473824` = TikTok Lite, `1340` = musically_go | Constant |
| `device_id` | Durable device identity, 19 digits | TikTok, at register |
| `iid` | Install ID, pairs with device_id | TikTok, at register |
| `cdid` | Client device ID (UUID you generate) | You |
| `openudid` | 16 hex characters you generate | You |
| `license_id` | Feeds X-Ladon key schedule | Constant per app |
| `version_code` | App build — gates which endpoints answer | You choose |

**Registration payload** is JSON (app header + device header + custom block) encrypted with **TTEncrypt** (TikTok's own byte-level body cipher), posted as `application/octet-stream;tt-data=a`.

Device profiles must be **internally consistent**: a Samsung SM-A136U has a specific screen resolution, DPI, ABI, Android version range, and carrier set. The developer built a catalogue of **~250 real Android device profiles** crossed with a **carrier table of ~2,000 MCC/MNC pairs** derived from public numbering-plan data.

**Bootstrap problem:** You need a working signature to register, and signing needs a device. Solution: bootstrap with client-generated fields (cdid, openudid) and zeros where the issued fields go.

Successful registration returns:
```json
{ "device_id_str": "7680616891110524437", "install_id_str": "7680617333853718293", "new_user": true }
```

**Survival rate:** 60–95% of registration attempts succeed, depending almost entirely on proxy quality.

---

### 1.3 The Activation Call (Critical — Unknown to Most)

After registration, most endpoints answer. But `/aweme/v1/user/profile/other/` (full profile) returns empty 200 **every single time** without this extra step:

```
GET /service/2/app_alert_check/?&cronet_version=...&ttnet_version=...&tt_info=<TTEncrypt+base64>
→ { "message": "success" }
```

This is the call the real app makes on first launch — telemetry that marks the device as a **running app**, not just a bare registration. Without it:

| Device generation | Profile endpoint |
|---|---|
| Register only | 0/360 (empty 200, every time) |
| Register + startup call | 100/100 |

The `tt_info` blob contains ~60 key=value pairs (GAID, timezone, install ID, device ID, carrier, screen, ABI, locale, request UUID) TTEncrypt-ed and base64url-encoded.

**This is not documented anywhere. It is not visible in a signature dump. It does not fail loudly.**

---

### 1.4 Device Proving (Three-Stage Pipeline)

After activation, the pipeline adds a **proof step** — a real read against a known creator. If content comes back, the device joins the pool. If not, it is **discarded** (not retried, not quarantined).

```
Register → Activate → Probe (profile endpoint) → Pool (or discard)
```

Without the filter: pool is a mixture of working and quietly dead devices; success rate drifts down invisibly over days. With the filter: pool is uniformly capable by construction.

Health is visible:
```
{ "live": 43, "generation_survival_rate": 0.9555, "success_total": ..., "failure_total": ... }
```

---

### 1.5 Request Anatomy & Signing

Every request carries **38 common parameters** describing the handset, carrier, region, and app build. Parameter order is **fixed** — sorting alphabetically (as Go's `url.Values.Encode()` does) silently produces an invalid signature.

**The five signature headers:**

| Header | Binds | Difficulty |
|---|---|---|
| `X-Khronos` | Unix seconds — replay bound | None (it's a timestamp) |
| `X-Ss-Stub` | MD5 of the request body | None (POSTs only) |
| `X-Gorgon` | Legacy digest over URL, body, time | Low — public write-ups exist |
| `X-Ladon` | Timestamp + license_id + app_id | Moderate — Speck-128/256 |
| `X-Argus` | Everything, bound to the device | **High** — protobuf, two cipher layers, no feedback |

**Two critical properties:**
- The signature covers the **entire query string** (not just the path). Change `count=20` to `count=21` and you recompute from scratch.
- The signature is **bound to one specific device**. You cannot sign with device A and send device B's identifiers.

---

### 1.6 X-Argus — The Hard One

X-Argus is not a string hash. Its plaintext is a **proto3 protobuf message** containing:

```protobuf
marker          // fixed marker
nonce           // per-request random, 0x10000000..0xFFFFFFFF
aid             // "1233" / "473824"
timestamp       // X-Khronos again, inside the blob
BodyHash        // SM3 of the body (16 zero bytes on GET)
QueryHash       // SM3 of the literal query string
AlgorithmCount.SignCount  // counter of how many requests this install has made
```

The `SignCount` is specifically designed so that naive replay is detectable in aggregate — a real phone's counter climbs steadily over the life of the install.

**Encryption pipeline (in order):**
1. Serialize protobuf
2. Key derivation — per-`aid` 32-byte constant signing key
3. Simon cipher (inner layer)
4. XOR mix
5. Byte reversal
6. Framing — version byte, entropy, 3-byte marker from SM3 digests
7. AES-128-CBC (outer layer)
8. Base64 encode

Two encryption layers with different primitives, different key derivations, with a byte reversal and XOR sandwiched between them. **There is no feedback** — get step 6 wrong and you produce a perfectly well-formed header that TikTok answers with empty 200.

---

### 1.7 Cryptographic Primitives Used

#### Simon (inner cipher — lightweight ARX)
- Published by NSA in 2013
- ARX construction: Addition, Rotation, XOR only — no S-boxes, no lookup tables
- Used in 128/256 configuration: 256-bit key, 128-bit block, 72 rounds
- Round constants from Z4 sequence (62-bit LFSR period)
- Compiles to almost nothing on ARM — designed to be small and avoid cache-timing side channels
- **Not in any standard library** — must be custom-implemented

#### Speck (X-Ladon — lightweight ARX)
- Also NSA, also ARX
- 128/256 configuration: 256-bit key, 34 rounds
- Key schedule reuses the round function — wrong word order or endianness gives 32 valid-looking but incorrect round keys
- **Not in any standard library**

#### SM3 (hash — Chinese national standard)
- GB/T 32905-2016 — Chinese national cryptographic hash standard
- 256-bit output, 512-bit blocks, Merkle-Damgård
- Similar to SHA-256 but with two parallel message expansion schedules and a different round function
- **Absent from every Western standard library**
- Many reference implementations floating around are wrong (two message expansion arrays `W` and `W'` are trivially transposable)

#### TTEncrypt (body cipher)
- Not a standard construction — TikTok's own fixed-key byte transform with a small lookup table
- Not cryptographically serious; exists only to stop casual traffic inspection
- Used for registration payload and activation blob
- Easiest of the four to reimplement

#### AES-128-CBC (outer layer of X-Argus)
- Standard — the interesting design choice is that AES is the outer layer while Simon (non-standard) is the inner layer actually protecting the protobuf

---

### 1.8 X-Ladon (Simpler Gate)

```
4 random bytes + MD5 + Speck-128/256 encryption of a dash-joined string
Random bytes prepended to output so server can rederive the key
```

Filters out anyone who hasn't looked at the app at all, costs approximately nothing to verify at scale. Argus is the expensive check that runs after.

---

### 1.9 Version Gating

A correct signature is **necessary but not sufficient**. Some endpoints are gated on the client build server-side:

| App build | `/aweme/v2/comment/list/` |
|---|---|
| 32.8.2 (320802) | empty 200 |
| 35.5.4 (350504) | 178 KB of comments |

The version bump also unlocked comment replies and follower listing. The endpoint catalogue records the exact build each endpoint needs, and the server swaps the four version fields transparently before signing:

```go
func versionFor(endpoint string) string { return versionTable[endpoint] }
```

Pinning the newest build everywhere is **wrong** — newer builds tighten other checks. Each endpoint must use the specific build that works for it.

---

### 1.10 Region Partitioning

TikTok runs several regional data centres, and **they do not serve the same endpoints to the same devices**:

| Host | Fresh device, profile detail | Response |
|---|---|---|
| `api16-normal-useast5.tiktokv.us` | 50/50 | 9,517 bytes |
| `api16-normal-c-alisg.tiktokv.com` | 1/50 | empty 200 |
| `api16-normal-c-useast1a.tiktokv.com` | 0/50 | empty 200 |

Key regional hosts:
- `alisg` — Singapore (`api16-normal-c-alisg.tiktokv.com`) — serves most endpoints
- `useast5` — US East (`api16-normal-useast5.tiktokv.us`) — **only host that serves user.info to fresh devices**
- `useast1a` — US East 1A (`api16-normal-c-useast1a.tiktokv.com`) — only host for `music.info`

The host is **part of the endpoint definition**, established by measurement (not documentation). The catalogue stores a host per route.

**Secondary effect:** The device's registered region influences content on region-scoped endpoints (trending sounds, trending categories). Running pools registered in `US` vs `BR` gives genuinely different charts from identical code — how you get per-country data without per-country code.

---

### 1.11 TLS Fingerprint (JA3)

Before any HTTP bytes arrive, the TLS ClientHello is a fingerprint. JA3 = MD5 of 5 comma-joined fields (TLS version, cipher list, extensions, elliptic curves, EC point formats). Libraries are highly distinguishable by their JA3.

**Go's `crypto/tls` has a very distinctive JA3** — and no Android app has ever emitted it, because Android apps use BoringSSL through OkHttp. TikTok's `useast5` edge checks.

**Empirical proof:**
```
Same request, three clients, back-to-back:
Python (requests):  9,517 bytes  ← works
curl:               9,519 bytes  ← works
Go (crypto/tls):    0 bytes      ← HTTP 200 empty
```

**Fix:** [uTLS](https://github.com/refraction-networking/utls) — lets you specify the exact ClientHello:

```go
HelloAndroid_11_OkHttp  // profile selection — one line
// NextProtos pinned to "http/1.1" — NOT h2 even though Android profile advertises h2
```

Result: profile detail on fresh devices went from **0% to 100%**.

**The Go proxy trap:** `http.Transport` **ignores `DialTLSContext` when `Proxy` is set** — it dials the proxy, issues CONNECT itself, then runs its own standard-library handshake over the tunnel. Your custom dialer is silently discarded. You must handle the proxy CONNECT tunnel manually before the uTLS handshake.

---

### 1.12 Empty 200 Detection Logic

```go
if status != 200        → return error "upstream HTTP %d"
if len(body) < 64      → return error "empty upstream body (%d bytes)"
if !json.Valid(body)   → return error "upstream body is not a JSON object"
if status_code != 0    → return error "upstream status_code %d"
```

**Non-retriable TikTok status codes:**

| `status_code` | Message | Treatment |
|---|---|---|
| 2065 | User doesn't exist | 404, no retry |
| 3170 | user not exists | 404, no retry |
| 3002060 | Profile user is hiding following list | 403, no retry |

---

### 1.13 Keep-Alive vs. Fresh Connection Strategy

Rate limiting is **per exit IP**. HTTP keep-alive pins you to one exit IP for the life of the TCP connection. A rotating proxy assigns a **new exit IP per TCP connection**. Naive retries over a keep-alive connection all go from the same blocked IP.

| Configuration | Success Rate | Bottleneck |
|---|---|---|
| Keep-alive everywhere | 88.2% | Retries reuse the blocked IP |
| Keep-alive nowhere | 96.2% | Proxy gateway handshake storm (`466 Too Many Requests`) |
| **Keep-alive on first attempt only, fresh connection on retry** | **99.3%** | None |

Measured over hundreds of millions of calls across four shards.

```go
// First-attempt pool: keep-alive (common case costs no handshake)
// Retry pool: DisableKeepAlives=true => fresh TCP => NEW exit IP
if isRetry { transport.DisableKeepAlives = true }
```

---

## 2. Infrastructure

### 2.1 Implementation Language & Architecture

- **Language:** Go 1.24
- **Architecture:** Self-hosted Go service — one binary, no database, no queue, no emulator, no native library
- **Reference data** (device profiles, carrier table, endpoint catalogue) is compiled in
- **Cold start:** 15–60 seconds for initial device pool generation; pool persists to disk so restarts are instant
- **Minimum compute:** Collection layer runs comfortably on 2 cores; the database is the resource-intensive part

### 2.2 Scale Configuration for Billion-Scale Run

The three-week run that produced 5.94 billion videos used:
- **4 shards** running in parallel
- **Residential proxy tier** (~$950/month flat rate, unmetered pool)
- Horizontal scaling: another subscription + another instance, nothing in the code changes

### 2.3 Proxy Setup

**Mandatory, not optional** — rate limiting is per exit IP, and retries are structurally useless without IP rotation.

**Verification check:**
```bash
for i in 1 2 3; do curl -s https://ip.me; done
# Different IP each time = rotating, good
```

| Tier | Specs | Cost | Realistic for |
|---|---|---|---|
| Rotating datacenter | 100 concurrent threads, 200 Mbit/s | ~$150/month | **Millions of records** |
| Unlimited residential | Unmetered residential pool | ~$950/month | **Billions** |

**Key requirements:**
- Rotating, with a single gateway endpoint
- Published thread limit
- Flat rate (not metered — metered plans punish exactly the most valuable endpoints)
- Country targeting for regional charts (device region and exit region should agree)
- Trial first: generate 30 devices, read `generation_survival_rate` before committing

**Proxy selection notes:**
- Don't pay by the gigabyte — a page of videos is 1.1 MB, a page of recommended creators is 2.9 MB
- A static proxy is no better than no proxy
- Registration success rate varies significantly between providers advertising the same product

### 2.4 Throughput (at $150/month datacenter tier, 100 threads, 200 Mbit/s)

| Endpoint | Per response | Binding limit | Ceiling |
|---|---|---|---|
| Creator profiles (user.info) | 9.5 KB | Threads | ~140/s · ~12M/day |
| Comments (20/page) | 174 KB | Threads | ~1,600/s · ~140M/day |
| Followers (20/page) | 178 KB | Threads | ~1,600/s · ~140M/day |
| Videos with full metadata (20/page) | 1.1 MB | **Line speed** | ~450/s · ~39M/day |
| Creator graph walk (user.recommended) | 2.9 MB | **Line speed** | ~350/s · ~30M/day |

### 2.5 Database: ClickHouse

Used for storage at billion-row scale. Critical lessons learned:

1. **Partition keys:** `author_id % 8` caused a 43x spread between partitions (TikTok platform IDs are not uniformly distributed). **Hash the ID before the modulus** to flatten it.
2. **Update path:** `ReplacingMergeTree` keeps the newest whole row. Write a partial update and every field you left out is silently blanked. No errors.
3. **Duplicate control:** One table was carrying 3× the rows it needed before it became visible; rebuilding returned several terabytes.
4. **System log retention:** ClickHouse writes `text_log` and `trace_log` with no retention by default. They reached **243 GB** on one instance and filled a 7 TB volume — stopping all writes. **TTL on system tables is not optional.**

---

## 3. What Data Can Be Collected

### 3.1 The 24 Endpoints

All 24 routes are GET, all take query parameters, all return TikTok's JSON unmodified.

#### Creators

| Route | Parameters | Returns |
|---|---|---|
| `/v1/user/posts` | user_id, count, max_cursor | Videos, each with the full author object |
| `/v1/user/info` | user_id, sec_user_id | Full profile incl. `bio_email`, links, commerce flags |
| `/v1/user/followers` | user_id, sec_user_id, count, max_time | Follower list |
| `/v1/user/following` | user_id, sec_user_id, count, max_time | Following list (where published) |
| `/v1/user/recommended` | user_id, sec_user_id, count | TikTok's own similar-creators graph |

#### Videos

| Route | Parameters | Returns |
|---|---|---|
| `/v1/video/info` | aweme_id | Media, stats, sound, tags, author |
| `/v1/video/comments` | aweme_id, count, cursor | Comments with commenter's user object |
| `/v1/video/comments/replies` | aweme_id, comment_id, count, cursor | Second level of comment tree |

#### Sounds

| Route | Parameters | Returns |
|---|---|---|
| `/v1/music/info` | music_id | Sound detail incl. `user_count` |
| `/v1/music/posts` | music_id, count, cursor | Popular videos using the sound |
| `/v1/music/posts/fresh` | music_id, count, cursor | Newest videos using the sound |
| `/v1/music/trending` | count, cursor | Trending sounds chart (per device region) |
| `/v1/music/related` | aweme_id, count, cursor | Sounds suggested for a video |

#### Hashtags & Search

| Route | Parameters | Returns |
|---|---|---|
| `/v1/hashtag/search` | keyword, count, cursor | Hashtag IDs with view counts |
| `/v1/hashtag/info` | hashtag_id | Hashtag detail |
| `/v1/hashtag/posts` | hashtag_id, count, cursor | Popular videos under the tag |
| `/v1/hashtag/posts/fresh` | hashtag_id, count, cursor | Newest videos under the tag |
| `/v1/search/videos` | keyword, count, offset | Videos |
| `/v1/search/general` | keyword, count, offset | Blended creators, videos, and tags |
| `/v1/search/music` | keyword, count, cursor | Sounds |
| `/v1/search/users` | keyword, count, cursor | Handle or name → numeric `user_id` |

#### Discovery

| Route | Parameters | Returns |
|---|---|---|
| `/v1/trending/categories` | count, cursor | App's what-is-hot shelves |
| `/v1/trending/effects` | count, cursor | Videos with `sticker_detail` for trending effects |
| `/v1/feed` | count, max_cursor | Anonymous For You feed (10% success rate — weak) |

### 3.2 Measured Success Rates

Measured: 100 calls each, max 4 attempts, against freshly generated pool over rotating proxy gateway.

| Endpoint | Success | Avg attempts | Avg response |
|---|---|---|---|
| user.info | **100%** | 1.00 | 9 KB |
| user.recommended | **100%** | 1.08 | 2.9 MB |
| music.posts | **100%** | 1.06 | 1.7 MB |
| music.posts_fresh | **100%** | 1.34 | 1.7 MB |
| music.trending | **100%** | 1.00 | 85 KB |
| music.related | **100%** | 1.00 | 139 KB |
| hashtag.info | **100%** | 1.00 | 3.8 KB |
| hashtag.posts_fresh | **100%** | 1.00 | 1.3 MB |
| search.general | **100%** | 1.06 | 527 KB |
| search.music | **100%** | 1.11 | 100 KB |
| search.users | **100%** | 1.00 | 86 KB |
| trending.categories | **100%** | 1.07 | 380 KB |
| trending.effects | **100%** | 1.10 | 232 KB |
| video.comment_replies | **100%** | 1.05 | 8 KB |
| video.info | 94% | 1.96 | 58 KB |
| user.following | 93% | 1.90 | 23 KB |
| user.followers | 92% | 2.12 | 178 KB |
| video.comments | 92% | 2.02 | 174 KB |
| search.videos | 92% | 1.82 | 639 KB |
| user.posts | 90% | 2.26 | 1.1 MB |
| music.info | 90% | 2.15 | 12 KB |
| hashtag.posts | 89% | 2.17 | 1.3 MB |
| hashtag.search | 78% | 2.16 | 11 KB |
| **feed.recommended** | **10%** | 3.93 | 248 KB |

`feed.recommended` is genuinely weak — an anonymous device with no watch history asking for a personalised feed is exactly the traffic TikTok most wants to throttle. It's dominated by honest 429s.

### 3.3 Fields Available from the API (vs. Web)

The mobile API returns far more than the web layer:

| Field | Where | Populated |
|---|---|---|
| `statistics.collect_count` | Any video | Always — **saves**, often the earliest movement signal |
| `music.user_count` | Any sound | Always — videos made with the sound |
| `author.ins_id` | Video author object | ~26% of creators |
| `author.youtube_channel_id` | Video author object | ~19% |
| `bio_email` | `user.info` only | ~1% |
| `commerce_user_level` | `user.info` | Always |
| Bio link | *Neither API* | **0% — not in mobile API at all** (web-surface only) |

**Notable:** One `user.posts` request returns 20 videos **and** the full creator record. On the web, that's 21 requests.

### 3.4 What's Out of Reach

Everything account-gated is permanently inaccessible:
- Your own DMs
- Private videos
- Who liked what
- Any authenticated/session-specific data

"No amount of tuning gets you there."

---

## 4. Free vs. Paid Offerings

### Free (No Cost)

- **Full technical write-up** at https://tiktok-api.seeksocial.io (~30-minute read)
- **4.5 billion-row TikTok video dataset** on HuggingFace (https://huggingface.co/datasets/kuben-developer/tiktok-videos-4b)
  - 27 Parquet files, zstd compressed, ~289 GB total
  - One row per video, deduplicated on `content_id`
  - Schema: `content_id`, `create_time`, `desc`, `mentions`, `duration`, `is_video`, `music_id`, `music_title`, `views`, `likes`, `comments`, `shares`, `saves`, `country`, `language`, `is_ad`
  - **Note:** No author IDs, usernames, or profile data included (deliberate); no media URLs (they expire within days)
  - Coverage: 27 of 32 storage partitions (unbiased ~84% sample)

### Paid: Repository Access ($699 one-time)

Available immediately with no waitlist.

**Includes:**
- Full signing stack: Simon, Speck, SM3, TTEncrypt, X-Argus, X-Ladon — with per-primitive test vectors
- Device registration, activation, and proving pipeline
- uTLS transport with manual proxy tunnel
- All 24 endpoints, measured and documented
- Pool management: health, eviction, rotation, persistence
- Docker image and compose file
- Live integration test suite with seed discovery
- Python, Node, curl, and `.http` clients
- Generated reference docs for every endpoint
- Reliability, pagination, and error engineering guides
- Lifetime updates to the same repository
- Direct support line during setup

**Purchase flow:** Checkout asks for GitHub username; repository invitation goes to that account automatically, normally within a minute.

**Buy link:** https://buy.stripe.com/5kQ6oH7sn9s573b5C95J60q

### Paid: Done-for-You Setup ($1,899 one-time, currently full/waitlist)

Everything in $699 tier **plus**:
- Full collection system built on **your server** from a clean box
- Database architecture sized to your volume (engine choice, partition/sort keys, update path, denormalisation)
- ClickHouse installed, tuned and sized, with system log retention configured
- Crawl pipeline: discovery, work queues, resume-after-failure, deduplication
- Sharded across multiple instances and proxy capacity
- Proxy plan chosen, configured, and rotation-verified
- Concurrency and retry budget tuned to your actual plan
- Device pool generated and sized to workload
- Monitoring: freshness, write failures, pool health, disk
- Full smoke test: all 24 endpoints returning live data
- Live walkthrough of endpoints and pagination
- 7 days of post-handover support

**Note:** Server and proxy subscription are **yours** — not included in the price, not shared with the developer.

---

## 5. Pricing Summary

| Product | Price | Availability |
|---|---|---|
| Dataset (HuggingFace) | **Free** | Available |
| Technical write-up | **Free** | Available |
| Repository access (code only) | **$699 one-time** | Available now |
| Done-for-you setup | **$1,899 one-time** | Currently full (waitlist) |
| Rotating datacenter proxy (recommended 3rd party) | ~$150/month | External |
| Unlimited residential proxy (billion-scale) | ~$950/month | External |

---

## 6. Use Case Example: Sound Trend Detector

The write-up includes a complete worked example showing the data's practical value:

1. **Snapshot trending sounds hourly** via `/v1/music/trending` → track `user_count` (videos made with each sound)
2. **Diff consecutive snapshots** to measure growth rate
3. **Confirm acceleration** via time-spread of recent videos using the sound (`/v1/music/posts/fresh`)
4. **Identify who's driving it** — author object embedded in every video response, no extra requests needed
5. **Multi-region**: Run separate pools registered in US, BR, etc. → independent charts from identical code

**High fresh-clustering + low cumulative plays = sound on the way up** (before it's obviously trending)

Rate: ~200 requests/hour for 50 candidates — essentially free at any proxy tier.

---

## 7. Legal & Compliance Notes

- **Against TikTok's Terms of Service** — sold for research and educational use only
- **GDPR/CCPA applies** regardless of collection method — personal data on real people
- Dataset card explicitly bans identifying, profiling, targeting, or contacting individuals
- Author acknowledges: "not open source" was wrong word — it's public data released as-is

---

## 8. Developer Profile & Contact

- **Reddit:** u/DataShack (r/MachineLearning, r/datasets)
- **HuggingFace:** kuben-developer
- **Site:** https://tiktok-api.seeksocial.io
- **Project duration:** ~2 years of development on the codebase
- **Scale demonstrated:** 5.94B videos + 3.23B profiles + 2.8B comments in 3 weeks
- **Openness:** Will upload data to S3 and share directly if HuggingFace removes it

---

## 9. Relevance to CreatorLookup

### Why This Is Valuable for Creator Discovery

1. **`user.recommended` endpoint** — TikTok's own similar-creator graph (2.9 MB per response, 100% success rate). This is TikTok's internal "creators like this one" signal, invaluable for niche mapping.
2. **Saves (`statistics.collect_count`)** — often the earliest engagement signal, not available on the web
3. **`commerce_user_level`** — always present on user.info, flags commercial intent
4. **`author.ins_id` + `author.youtube_channel_id`** — cross-platform linkage on ~25% and ~19% of creators
5. **`bio_email`** on ~1% of creators — direct contact
6. **Trending sounds + creator attribution** — find who's driving trends before the trend peaks
7. **Regional data** — different device pools for different markets, same code

### Partnership/Hire Considerations

- Developer is clearly technically sophisticated (custom crypto implementations, production billion-scale systems, database ops)
- Sells the code for $699, does consulting for $1,899 — both very affordable for a SaaS deal
- "Done for you" tier is currently full but can be waitlisted
- Would be worth reaching out via Reddit (u/DataShack) to discuss a custom arrangement
- The system runs anonymously (no TikTok accounts), so there's nothing to get banned

---

*Document compiled from: tiktok-api.seeksocial.io, huggingface.co/datasets/kuben-developer/tiktok-videos-4b, r/MachineLearning post by DataShack. Measurements re-run September 2026.*
