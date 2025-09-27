CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    name TEXT,               -- Changed from VARCHAR to TEXT
    location TEXT,           -- Changed from VARCHAR to TEXT
    date TEXT,               -- Changed from DATE to TEXT
    rating TEXT,             -- Changed from FLOAT to TEXT
    review TEXT,             -- Unchanged, remains TEXT
    vector FLOAT8[]          -- Remains as FLOAT8 array
);
