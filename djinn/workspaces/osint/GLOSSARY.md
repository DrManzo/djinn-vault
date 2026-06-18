# OSINT GLOSSARY

> Terminology reference for the OSINT Intelligence Department. Short definitions, no fluff.

---

## Collection Disciplines

**OSINT** — Open-Source Intelligence. Intelligence derived exclusively from publicly available sources: web, social media, public records, published documents. No hacking, no unauthorized access.

**OSINT+** — OSINT augmented with lightly gated sources: data brokers, aggregator APIs, breach databases with public tiers. Still legal, but requires awareness of ToS boundaries.

**Open-source** — Publicly available without authentication or payment. The core scope of OSINT.

**Closed-source** — Proprietary, paywalled, or access-restricted data. Not OSINT. Examples: Palantir feeds, law enforcement databases, private breach dumps.

**HUMINT** — Human Intelligence. Information gathered from human sources — interviews, social engineering, informants. Out of scope for automated Djinn ops; flag for operator if human contact is needed.

**SIGINT** — Signals Intelligence. Intelligence from intercepted electronic communications. Passive monitoring of public signals (e.g., public radio, open Wi-Fi beacon data) is borderline OSINT; active interception is illegal without authorization.

**SOCMINT** — Social Media Intelligence. OSINT subset focused on social platforms: posts, connections, metadata, behavioral patterns from publicly accessible social media.

**IMINT** — Imagery Intelligence. Intelligence derived from images and satellite/aerial photography. Includes reverse image search, geolocation from photos, and public satellite imagery (Google Maps, Sentinel Hub).

**FININT** — Financial Intelligence. Intelligence from public financial records: SEC filings, corporate registrations, bankruptcy records, property records, publicly disclosed transactions.

---

## Operational Concepts

**Passive OSINT** — Collection with zero interaction with the target or target's infrastructure. Search engines, cached pages, public APIs, archived data. Leaves no trace on target systems. Gateway Tier 0–1.

**Active OSINT** — Collection that touches target infrastructure: port scans, direct HTTP requests to target servers, account enumeration via live platform APIs. May leave traces. Gateway Tier 2–3.

**Footprinting** — Mapping the external-facing surface of a target: domains, subdomains, IP ranges, email patterns, public employee data, technology stack. First phase of most ops.

**Fingerprinting** — Identifying specific versions, configurations, or implementations of software/hardware on target systems. Usually active (Tier 2–3). Example: identifying a web server version from banner data.

**Pivoting** — Using one confirmed data point to find related data points. Example: email → domain → IP → ASN → other domains on same ASN. The core analytical motion of OSINT.

**Entity resolution** — Determining whether two data points refer to the same real-world entity. Example: confirming that @handle_xyz and email john.doe@company.com belong to the same person.

**Link analysis** — Mapping relationships between entities: person→organization, email→domain, handle→platform. Produces org charts, social graphs, and infrastructure maps.

**Deconfliction** — Resolving contradictions between two or more sources that disagree on the same fact. Never resolve by assumption — flag the contradiction and note both versions with their sources.

---

## Tradecraft

**OPSEC** — Operational Security. Practices that prevent the operator's identity or collection activities from being exposed to the target or third parties.

**OPSEC failure** — Any action that reveals the operator's identity, intent, or methods to the target. Examples: logging into a target's platform while collecting, visiting a target's site from an unmasked IP, leaving search history tied to your identity.

**Legend** — A cover identity constructed to support a persona. Includes backstory, consistent behavioral history, and supporting accounts. Full legends are Tier 4 — operator approval required.

**Persona** — A semi-anonymous identity used for passive monitoring. Less developed than a legend. Example: a generic social media account with no personal details used to view public posts.

**Sock puppet** — A fabricated online identity used to interact with targets or their communities. Any interaction with a target via sock puppet is Tier 3+. Passive use (monitoring only) may be Tier 1–2 depending on platform ToS.

---

## Data Quality

**Confidence scoring** — A three-tier rating assigned to each finding:
- **High** — Confirmed by 2+ independent primary sources, no contradictions
- **Medium** — Confirmed by 1 primary source or 2+ secondary sources
- **Low** — Single secondary source, unverified, inferred, or circumstantial

**Source reliability matrix** — NATO standard for rating sources and information independently:

| Code | Source Reliability | Code | Information Accuracy |
|---|---|---|---|
| A | Completely reliable | 1 | Confirmed by other sources |
| B | Usually reliable | 2 | Probably true |
| C | Fairly reliable | 3 | Possibly true |
| D | Not usually reliable | 4 | Doubtful |
| E | Unreliable | 5 | Improbable |
| F | Reliability cannot be judged | 6 | Truth cannot be judged |

Example: A source rated `B/2` is usually reliable and the information is probably true. A source rated `F/6` is unclassified noise — log it but do not act on it without corroboration.

---

*GLOSSARY — OSINT / Djinn system — maintained by SCRIBE*
