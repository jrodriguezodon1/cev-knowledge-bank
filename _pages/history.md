---
layout: default
title: "All Entries"
permalink: /history/
---

<div class="domain-header">
  <h1 class="page-title">🕐 All Entries</h1>
  <p class="page-subtitle">Everything, sorted newest first.</p>
</div>

{% assign all_docs = site['paid-ads'].docs | concat: site['influencer-marketing'].docs | concat: site['dev-engineering'].docs | concat: site['dev-technical'].docs | concat: site['product-gtm'].docs | concat: site['ai-agents'].docs | concat: site['founder-business'].docs | concat: site['life-personal'].docs | concat: site['attribution-mmm'].docs | concat: site['business-strategy'].docs | concat: site['content-marketing'].docs %}
{% assign sorted_docs = all_docs | sort: 'date' | reverse %}

<!-- All unique tags -->
{% assign all_tags_arr = "" %}
{% for doc in all_docs %}
  {% if doc.tags %}
    {% for tag in doc.tags %}
      {% assign all_tags_arr = all_tags_arr | append: tag | append: "||" %}
    {% endfor %}
  {% endif %}
{% endfor %}
{% assign tag_list = all_tags_arr | split: "||" | uniq %}

<div class="filter-bar">
  <input type="text" id="searchInput" class="search-input" placeholder="Search…">
  <button class="tag-filter-btn active" data-tag="all">All</button>
  {% for tag in tag_list %}
    {% unless tag == "" %}
    <button class="tag-filter-btn" data-tag="{{ tag }}">{{ tag }}</button>
    {% endunless %}
  {% endfor %}
</div>

<div class="entries-list">
  {% for doc in sorted_docs %}
  {% assign doc_tags = doc.tags | join: "," | default: "" %}
  <a href="{{ doc.url | relative_url }}" class="entry-card" data-tags="{{ doc_tags }}">
    <div class="entry-card-top">
      <span class="entry-card-title">{{ doc.title }}</span>
      <span class="entry-card-date">{{ doc.date | date: "%b %d, %Y" }}</span>
    </div>
    {% assign excerpt_text = doc.content | strip_html | truncatewords: 18 %}
    <div class="entry-card-excerpt">{{ excerpt_text }}</div>
    <div class="entry-card-bottom">
      {% if doc.category %}
      <span class="entry-category-badge cat-{{ doc.category }}">{{ doc.category }}</span>
      {% endif %}
      {% if doc.tags %}
        {% for tag in doc.tags limit:3 %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      {% endif %}
    </div>
  </a>
  {% endfor %}
</div>
