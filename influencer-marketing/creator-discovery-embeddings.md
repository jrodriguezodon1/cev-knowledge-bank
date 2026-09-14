# Creator Discovery — Embeddings & Vector Search

**Source:** Jose's r/influencermarketing Reddit comment + internal product thinking (Sep 2026)
**Added:** 2026-09-10
**Tags:** creatorlookup, embeddings, vector-search, discovery, moat

## The Insight
Most influencer DBs do keyword matching + metadata filtering. That's table stakes and commoditizing fast.

Real unlock: encode creator content into a vector space → semantic nearest-neighbor search.

## How It Works
1. Scrape creator content (captions, transcripts from Reels/TikToks/YT)
2. Embed each creator using OpenAI embeddings (or similar)
3. Store in pgvector (Supabase supports this natively)
4. User inputs seed creator or describes what they want → nearest-neighbor search
5. Layer audience overlap scoring to de-dupe reach

## The Alpha: Audience Overlap
Find creators whose audiences are near-identical to your best performer but with ZERO audience overlap. Reach new people who look exactly like your best customers. That's the actual moat.

## Competitive Landscape (Sep 2026)
- Modash, Influencersclub, Favikon — none have built this yet
- The ones that have are quietly printing
- This is the moat CL should build toward — not better filters, semantic similarity

## Status
scraper.creatorlookup.com is the backend. pgvector + embedding layer = next build priority.
