---
layout: default
title: Home
---

<div class="hero">
  <h1>What I'm learning</h1>
  <p>{{ site.documents.size }} entries across paid ads, AI agents, influencer marketing, and more.</p>
</div>

<!-- Domain grid -->
{% assign paid_ads_docs = site.documents | where: "category", "paid-ads" %}
{% assign im_docs = site.documents | where: "category", "influencer-marketing" %}
{% assign de_docs = site.documents | where: "category", "dev-engineering" %}
{% assign gtm_docs = site.documents | where: "category", "product-gtm" %}
{% assign ai_docs = site.documents | where: "category", "ai-agents" %}
{% assign biz_docs = site.documents | where: "category", "founder-business" %}
{% assign life_docs = site.documents | where: "category", "life-personal" %}

<div class="domain-grid">
  <a href="{{ '/paid-ads/' | relative_url }}" class="domain-card">
    <span class="domain-icon">📈</span>
    <div class="domain-label">Paid Ads</div>
    <div class="domain-count">{{ paid_ads_docs.size }} entries</div>
  </a>
  <a href="{{ '/influencer-marketing/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🤝</span>
    <div class="domain-label">Influencer Mktg</div>
    <div class="domain-count">{{ im_docs.size }} entries</div>
  </a>
  <a href="{{ '/dev-engineering/' | relative_url }}" class="domain-card">
    <span class="domain-icon">⚙️</span>
    <div class="domain-label">Dev & Eng</div>
    <div class="domain-count">{{ de_docs.size }} entries</div>
  </a>
  <a href="{{ '/product-gtm/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🚀</span>
    <div class="domain-label">Product & GTM</div>
    <div class="domain-count">{{ gtm_docs.size }} entries</div>
  </a>
  <a href="{{ '/ai-agents/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🤖</span>
    <div class="domain-label">AI Agents</div>
    <div class="domain-count">{{ ai_docs.size }} entries</div>
  </a>
  <a href="{{ '/founder-business/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🏗️</span>
    <div class="domain-label">Founder & Biz</div>
    <div class="domain-count">{{ biz_docs.size }} entries</div>
  </a>
  <a href="{{ '/life-personal/' | relative_url }}" class="domain-card">
    <span class="domain-icon">🌱</span>
    <div class="domain-label">Life & Personal</div>
    <div class="domain-count">{{ life_docs.size }} entries</div>
  </a>
</div>

<!-- Recent entries -->
{% assign all_docs = site.documents | sort: "date" | reverse %}

<!-- Collect all unique tags -->
{% assign all_tags_arr = "" %}
{% for doc in all_docs %}
  {% if doc.tags %}
    {% for tag in doc.tags %}
      {% assign all_tags_arr = all_tags_arr | append: tag | append: "||" %}
    {% endfor %}
  {% endif %}
{% endfor %}
{% assign tag_list = all_tags_arr | split: "||" | uniq | sort %}

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
  {% for doc in all_docs %}
  {% unless doc.path contains "_pages" %}
  {% assign doc_tags = doc.tags | join: "," | default: "" %}
  <a href="{{ doc.url | relative_url }}" class="entry-card" data-tags="{{ doc_tags }}">
    <div class="entry-card-top">
      <span class="entry-card-title">{{ doc.title }}</span>
      <span class="entry-card-date">{{ doc.date | date: "%b %d, %Y" }}</span>
    </div>
    {% assign excerpt_text = doc.content | strip_html | truncatewords: 18 %}
    <div class="entry-card-excerpt">{{ excerpt_text }}</div>
    <div class="entry-card-bottom">
      {% if doc.category %}<span class="tag category-tag">{{ doc.category }}</span>{% endif %}
      {% if doc.tags %}
        {% for tag in doc.tags limit:3 %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      {% endif %}
    </div>
  </a>
  {% endunless %}
  {% endfor %}
</div>
