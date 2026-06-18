# Feeds — README

This directory holds the passive intelligence feed registry. Feeds are always-on, operator-configured data streams that TREND monitors continuously without requiring an active operation.

---

## What Is a Feed?

A feed is a passive data source — an RSS, API endpoint, search alert, or webhook — that delivers ongoing signals about a topic, keyword, entity, or domain. Feeds run at Tier 0–1 (auto-approved) because they are read-only and require no active enumeration.

---

## Feed Types

| Type | Examples |
|---|---|
| RSS | News sites, blog feeds, press release wires |
| Google Alerts | Keyword and entity name monitoring |
| GitHub Activity | Star/fork/issue volume for tracked repos |
| Reddit RSS | Subreddit monitoring for keyword threads |
| Patent / Trademark | USPTO, EUIPO filing alerts |
| Domain Monitoring | WHOIS change alerts, new TLD registrations |
| Job Posting Alerts | LinkedIn, Indeed, Greenhouse for target orgs |

---

## How to Add a Feed

1. Open `feed-registry.md`
2. Add a new row to the feed table with: name, type, URL/query, target, added date
3. Assign to `TREND` for monitoring
4. Commit: `git commit -m "feeds(osint): add <feed-name> feed"`

---

## Directory Structure

```
feeds/
├── README.md           ← This file
└── feed-registry.md    ← All active feeds listed here
```
