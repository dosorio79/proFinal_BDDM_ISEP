-- Create the schema if it does not exist
CREATE SCHEMA IF NOT EXISTS testschema1;

-- Switch to the new schema
SET search_path TO testschema1;

-- Create DimDate table
CREATE TABLE IF NOT EXISTS DimDate (
    Date DATE PRIMARY KEY,
    Year INT,
    Month INT,
    Day INT,
    DayOfWeek INT
);

-- Populate DimDate table for all days in 2023 and 2024
INSERT INTO DimDate (Date, Year, Month, Day, DayOfWeek)
WITH RECURSIVE dates AS (
    SELECT '2023-01-01'::DATE AS Date
    UNION ALL
    SELECT (Date + INTERVAL '1 day')::DATE
    FROM dates
    WHERE Date + INTERVAL '1 day' <= '2024-12-31'
)
SELECT 
    Date,
    EXTRACT(YEAR FROM Date) AS Year,
    EXTRACT(MONTH FROM Date) AS Month,
    EXTRACT(DAY FROM Date) AS Day,
    EXTRACT(DOW FROM Date) AS DayOfWeek
FROM dates
ON CONFLICT (Date) DO NOTHING;

-- Create DimLocation table
CREATE TABLE IF NOT EXISTS DimLocation (
    LocationID INT PRIMARY KEY,
    Latitude FLOAT,
    Longitude FLOAT,
    Concelho VARCHAR(255),
    Freguesia VARCHAR(255),
    UNIQUE (Latitude, Longitude)
);

-- Create FactTwoWheel table
CREATE TABLE IF NOT EXISTS FactTwoWheel (
    ID SERIAL PRIMARY KEY,
    Date DATE,
    Latitude FLOAT,
    Longitude FLOAT,
    MeanOccupation FLOAT,
    PercentOccupation FLOAT,
    MinOccupation FLOAT,
    MaxOccupation FLOAT,
    TotalSpotNumber INT,
    LocationID INT,
    FOREIGN KEY (Date) REFERENCES DimDate(Date),
    FOREIGN KEY (LocationID) REFERENCES DimLocation(LocationID)
);
