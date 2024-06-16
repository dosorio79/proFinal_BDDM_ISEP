-- Join FactTwoWheel, DimLocation, and DimDate tables ensuring unique combinations
SELECT 
    ftw.ID AS FactID,
    ftw.Date AS FactDate,
    d.Year AS DimDateYear,
    d.Month AS DimDateMonth,
    d.Day AS DimDateDay,
    d.DayOfWeek AS DimDateDayOfWeek,
    dl.LocationID AS DimLocationID,
    dl.Latitude AS FactLatitude,
    dl.Longitude AS FactLongitude,
    dl.Concelho AS DimLocationConcelho,
    dl.Freguesia AS DimLocationFreguesia,
    ftw.MeanOccupation AS FactMeanOccupation,
    ftw.PercentOccupation AS FactPercentOccupation,
    ftw.MinOccupation AS FactMinOccupation,
    ftw.MaxOccupation AS FactMaxOccupation,
    ftw.TotalSpotNumber AS FactTotalSpotNumber
FROM 
    testschema1.FactTwoWheel ftw
JOIN 
    testschema1.DimDate d
ON 
    ftw.Date = d.Date
JOIN 
    testschema1.DimLocation dl
ON 
    ftw.LocationID = dl.LocationID
ORDER BY 
    ftw.Date, dl.LocationID
LIMIT 10;
