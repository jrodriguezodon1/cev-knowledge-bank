---
layout: default
title: "Product & GTM"
category: product-gtm
permalink: /product-gtm/
---

<div class="domain-header">
  <h1 class="page-title">🚀 Product & GTM</h1>
  <p class="page-subtitle">CL/Orbit product lessons, pricing, launch playbooks, competitors.</p>
</div>

{% assign domain_docs = site['product-gtm'].docs %}
{% assign sorted_docs = domain_docs | sort: 'date' | reverse %}

{% assign all_tags_arr = "" %}
{% for doc in domain_docs %}
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

{% if sorted_docs.size > 0 %}
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
      {% if doc.tags %}
        {% for tag in doc.tags limit:4 %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      {% endif %}
    </div>
  </a>
  {% endfor %}
</div>
{% else %}
<p class="empty-state">No entries yet in this domain.</p>
{% endif %}
