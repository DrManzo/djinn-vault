-- djinn/shipping/db_schema.sql
-- Run once to initialize shipping tables in the Djinn SQLite DB.
-- Both tables key to job_id (FK → job table).
--
-- Usage:
--   sqlite3 ~/.config/djinn/djinn.db < djinn/shipping/db_schema.sql

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------------------
-- shipment
-- One row per purchased EasyPost label.
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipment (
    shipment_id     TEXT        PRIMARY KEY,   -- EasyPost shipment ID
    job_id          INTEGER     NOT NULL,       -- FK → job.job_id
    tracking_code   TEXT,
    carrier         TEXT,                       -- e.g. "USPS"
    service         TEXT,                       -- e.g. "Priority"
    rate_usd        REAL        NOT NULL,
    label_url       TEXT,                       -- EasyPost URL (expires 24h)
    label_local     TEXT,                       -- local path after download
    created_at      TEXT        NOT NULL        -- ISO-8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_shipment_job ON shipment(job_id);

-- -------------------------------------------------------------------------
-- tracking_event
-- Append-only log of status updates from EasyPost webhooks or polling.
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tracking_event (
    event_id        INTEGER     PRIMARY KEY AUTOINCREMENT,
    shipment_id     TEXT        NOT NULL REFERENCES shipment(shipment_id),
    job_id          INTEGER     NOT NULL,
    status          TEXT        NOT NULL,   -- e.g. "in_transit", "delivered"
    detail          TEXT,
    event_time      TEXT        NOT NULL    -- ISO-8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_tracking_shipment ON tracking_event(shipment_id);
CREATE INDEX IF NOT EXISTS idx_tracking_job      ON tracking_event(job_id);

-- -------------------------------------------------------------------------
-- monthly_report view  (extends accounting spec)
-- Aggregates shipping cost per calendar month and adds it to net_income.
-- Replace `invoice` and `job` with your actual table names if different.
-- -------------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS monthly_shipping_summary AS
SELECT
    strftime('%Y-%m', s.created_at)          AS month,
    COUNT(s.shipment_id)                      AS total_shipments,
    ROUND(SUM(s.rate_usd), 2)                 AS total_shipping_cost,
    ROUND(AVG(s.rate_usd), 2)                 AS avg_shipping_cost
FROM shipment s
GROUP BY month
ORDER BY month DESC;
