---
layout: default
title: Home
---

<div class="hero">
  <h1>What I'm learning</h1>
  <p>{{ site.collections | map: 'docs' | join | size }} entries across paid ads, AI agents, influencer marketing, and more.</p>
</div>

<!-- Domain grid -->
<div class="domain-grid">
  <a href="{{ '/paid-ads/' | relative_url }}" class="domain-card">
    <span class="domain-icon">📈</span>
    <div class="domain-label">Paid Ads</div>
    <div class="domain-count">{{ site['paid-ads'].docs.size }} entries</div>
  </a>
  <a href="{{ '/influencer-marketing/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🤝</span>
    <div class="domain-label">Influencer Mktg</div>
    <div class="domain-count">{{ site['influencer-marketing'].docs.size }} entries</div>
  </a>
  <a href="{{ '/dev-engineering/' | relative_url }}" class="domain-card">
    <span class="domain-icon">⚙️</span>
    <div class="domain-label">Dev & Eng</div>
    <div class="domain-count">{% assign de_count = site['dev-engineering'].docs.size | plus: site['dev-technical'].docs.size %}{{ de_count }} entries</div>
  </a>
  <a href="{{ '/product-gtm/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🚀</span>
    <div class="domain-label">Product & GTM</div>
    <div class="domain-count">{{ site['product-gtm'].docs.size }} entries</div>
  </a>
  <a href="{{ '/ai-agents/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🤖</span>
    <div class="domain-label">AI Agents</div>
    <div class="domain-count">{{ site['ai-agents'].docs.size }} entries</div>
  </a>
  <a href="{{ '/founder-business/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🏗️</span>
    <div class="domain-label">Founder & Biz</div>
    <div class="domain-count">{% assign fb_count = site['founder-business'].docs.size | plus: site['attribution-mmm'].docs.size | plus: site['business-strategy'].docs.size %}{{ fb_count }} entries</div>
  </a>
  <a href="{{ '/life-personal/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🌱</span>
    <div class="domain-label">Life & Personal</div>
    <div class="domain-count">{{ site['life-personal'].docs.size }} entries</div>
  </a>
</div>

<!-- Recent entries -->
{% assign all_docs = site['paid-ads'].docs | concat: site['influencer-marketing'].docs | concat: site['dev-engineering'].docs | concat: site['dev-technical'].docs | concat: site['product-gtm'].docs | concat: site['ai-agents'].docs | concat: site['founder-business'].docs | concat: site['life-personal'].docs | concat: site['attribution-mmm'].docs | concat: site['business-strategy'].docs | concat: site['content-marketing'].docs %}
{% assign sorted_docs = all_docs | sort: 'date' | reverse %}
{% assign recent_docs = sorted_docs | limit: 10 %}

<!-- Collect all unique tags -->
{% assign all_tags = "" %}
{% for doc in all_docs %}
  {% for tag in doc.tags %}
    {% assign all_tags = all_tags | append: tag | append: "," %}
  {% endfor %}
{% endfor %}
{% assign tag_list = all_tags | split: "," | uniq | sort %}

<div class="filter-bar">
  <input type="text" id="searchInput" class="search-input" placeholder="Search entries…">
  <button class="tag-filter-btn active" data-tag="all">All</button>
  {% for tag in tag_list %}
    {% unless tag == "" %}
    <button class="tag-filter-btn" data-tag="{{ tag }}">{{ tag }}</button>
    {% endunless %}
  {% endfor %}
</div>

<div class="section-label">Recent</div>

<div class="entries-list">
  {% for doc in sorted_docs %}
  {% assign doc_tags = doc.tags | join: "," %}
  <a href="{{ doc.url | relative_url }}" class="entry-card" data-tags="{{ doc_tags }}">
    <div class="entry-card-top">
      <span class="entry-card-title">{{ doc.title }}</span>
      <span class="entry-card-date">{{ doc.date | date: "%b %d, %Y" }}</span>
    </div>
    {% assign excerpt_text = doc.content | strip_html | truncatewords: 18 %}
    <div class="entry-card-excerpt">{{ excerpt_text }}</div>
    <div class="entry-card-bottom">
      {% for tag in doc.tags limit:4 %}
      <span class="tag">{{ tag }}</span>
      {% endfor %}
    </div>
  </a>
  {% endfor %}
</div>
