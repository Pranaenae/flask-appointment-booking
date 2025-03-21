CREATE TABLE accounts(
  id SERIAL PRIMARY KEY , 
  username varchar(255),
  password varchar(255)
);

INSERT INTO users (username, password) 
VALUES('pranay', 'pranay@123');

CREATE TABLE appointments (
    date DATE PRIMARY KEY,
    total_appointments INT NOT NULL,  
    booked_appointments INT NOT NULL 
);

CREATE EXTENSION pg_cron;

CREATE OR REPLACE FUNCTION prefill_appointments(num_days_to_fill INT, num_total_appointments INT)
RETURNS VOID AS $$
DECLARE
    current_date DATE := CURRENT_DATE;
    target_date DATE;
BEGIN
    FOR i IN 0..(num_days_to_fill - 1) LOOP
        target_date := current_date + i;
        INSERT INTO appointments (date, total_appointments, booked_appointments)
        VALUES (target_date, num_total_appointments, 0)
        ON CONFLICT (date) DO NOTHING;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT cron.schedule(
    'prefill-appointments', -- Name of the cron job
    '0 0 * * *',           -- Cron schedule (midnight daily)
    $$SELECT prefill_appointments(10)$$ -- Function to execute (default_total = 10)
);

--View all jobs
SELECT * FROM cron.job;

SELECT prefill_appointments(10);