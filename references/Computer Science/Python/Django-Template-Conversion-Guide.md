---
title: "Django Template Conversion Guide"
created: 2026-05-19
modified: 2026-05-19
tags: [python, django, web-development, templates, mvt-architecture, static-files, template-inheritance]
source: "Perplexity AI Export"
category: "Computer Science/Python"
---

## Summary
A guide for converting static HTML files into production-ready Django templates, demonstrated through an HR Dashboard conversion. Covers template tags, template inheritance, static file organization, dynamic data binding from models, URL routing, and Django best practices for separating concerns.

## Key Points
- Static HTML can become Django templates with addition of template tags and dynamic data binding
- Template inheritance (`{% extends %}`, `{% block %}`) enables consistent UI across pages
- Static files (CSS/JS) must be separated into `/static/` directories
- Database models replace hardcoded data with dynamic query results
- URL reversal (`{% url %}`) prevents hardcoded links
- Complete conversion includes models, views, templates, static files, URLs, and settings
- Django admin provides built-in interface for managing content

## Details

### What Works in Static HTML
- HTML structure and semantic markup
- CSS styling and layout
- Overall design and appearance
- JavaScript functionality

### Required Modifications for Django

#### 1. Add Django Template Tags
```django
{% load static %}

{% for report in reports %}
  <tr>
    <td>{{ report.date }}</td>
    <td>{{ report.reporter }}</td>
    <td>{{ report.subject }}</td>
    <td>{{ report.department }}</td>
    <td>{{ report.status }}</td>
    <td><a href="{% url 'report-view' report.id %}">View</a></td>
  </tr>
{% endfor %}
```

#### 2. Separate Static Files
- Move styles to `/static/css/`
- Move scripts to `/static/js/`
- Reference in templates with `{% static 'css/style.css' %}`

#### 3. Implement Template Inheritance
```django
{% extends 'base.html' %}

{% block content %}
  <!-- Your dashboard content here -->
{% endblock %}
```

#### 4. Use Django URL Reversal
Replace hardcoded links:
```django
<!-- Before -->
<a href="/reports/42/">View</a>

<!-- After -->
<a href="{% url 'report-view' report.id %}">View</a>
```

#### 5. Dynamic Data Binding
- Replace hardcoded statistics with template variables
- Use `{% for %}` loops for database-driven tables
- Use `{% if %}` conditionals for status-dependent rendering

### Complete Django HR Dashboard Structure

#### Models
- `Report` model with fields: date, reporter, subject, department, status
- Status tracking (New, Under Review, Closed)
- Admin interface registration for easy content management

#### Views
- Dashboard view: Queries reports, passes to template
- Detail view: Shows individual report details
- Context dictionaries provide template variables

#### Templates
- `base.html`: Master template with common header/footer
- `dashboard.html`: Extends base, displays report table
- Template tags for loops, conditionals, URL reversal

#### Static Files
- `css/dashboard.css`: Dashboard-specific styling
- `js/export.js`: CSV export functionality
- Responsive design for mobile compatibility

#### URL Routing
- `urls.py` maps URLs to views
- Named URLs enable `{% url %}` template tag usage
- Clean URL patterns (e.g., `/reports/`, `/reports/<id>/`)

### Key Improvements Over Static HTML
- Dynamic data from database instead of hardcoded values
- Template inheritance for consistent UI across pages
- Django template tags (`{% for %}`, `{% if %}`, `{% url %}`)
- Color-coded status badges
- Responsive CSS for mobile-friendly design
- Proper static file organization
- Built-in Django admin for managing reports
- CSV export functionality via JavaScript

### Quick Start Setup
1. Copy document content into Django project files
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Add sample data through Django admin
5. Start development server: `python manage.py runserver`

## References
- Django Documentation: https://docs.djangoproject.com/
- Django Template Language Guide
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Python Programming Hub]]
- [[PyQt6 Modular UI Architecture]]
- [[Scrambled Notes to APA Essay Converter]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
- [[PyQt6-Modular-UI-Architecture]]
