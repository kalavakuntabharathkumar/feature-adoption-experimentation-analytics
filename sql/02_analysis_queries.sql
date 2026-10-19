-- 1. Event volume by day and event type
SELECT DATE_TRUNC('day', event_timestamp)::date AS event_date,
       event_name, COUNT(*) AS event_count,
       COUNT(DISTINCT user_id) AS unique_users
FROM events
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Experiment population balance
SELECT experiment_id, variant, COUNT(DISTINCT user_id) AS assigned_users
FROM experiment_assignments
GROUP BY experiment_id, variant
ORDER BY experiment_id, variant;

-- 3. Adoption outcome when an adopted flag has been loaded to a separate outcome table
-- Example outcome table schema: (experiment_id, user_id, adopted BOOLEAN)
SELECT a.experiment_id, a.variant,
       COUNT(*) AS assigned_users,
       COUNT(*) FILTER (WHERE o.adopted) AS adopted_users,
       AVG(o.adopted::int)::numeric(8,5) AS adoption_rate
FROM experiment_assignments a
JOIN experiment_outcomes o USING (experiment_id, user_id)
GROUP BY a.experiment_id, a.variant
ORDER BY a.experiment_id, a.variant;

-- 4. Daily active users
SELECT DATE_TRUNC('day', event_timestamp)::date AS event_date,
       COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_name = 'app_open'
GROUP BY 1 ORDER BY 1;
