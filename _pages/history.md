---
layout: default
title: "History"
permalink: /history/
---

<div class="domain-header">
  <h1 class="page-title">🕰 History</h1>
  <p class="page-subtitle">All entries, newest first.</p>
</div>

{% assign all_docs = site.documents | sort: "date" | reverse %}

<div class="filter-bar">
  <input type="text" id="searchInput" class="search-input" placeholder="Search all entries…">
</div>

{% if all_docs.size > 0 %}
<div class="entries-list">
  {% assign current_month = "" %}
  {% for doc in all_docs %}
    {% unless doc.path contains "_pages" %}
    {% assign doc_month = doc.date | date: "%B %Y" %}
    {% if doc_month != current_month %}
      {% assign current_month = doc_month %}
      <div class="month-divider">{{ doc_month }}</div>
    {% endif %}
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
{% else %}
<p class="empty-state">No entries yet.</p>
{% endif %}
