-- Read-only extraction for the FRRP baseline pilot (v0.1).
-- Source database: Global_Coral_Bleaching_Database_SQLite_11_24_21.db
-- Joins are kept one row per Sample_ID and observations are restricted to 2005-2016.

SELECT
    se.Sample_ID,
    se.Site_ID,
    se.Reef_ID,
    se.Date_Year,
    se.Date_Month,
    se.Date_Day,
    se.Depth_m,
    si.Latitude_Degrees,
    si.Longitude_Degrees,
    e.ClimSST,
    e.Temperature_Mean,
    e.SSTA,
    e.SSTA_DHW,
    e.TSA,
    e.TSA_DHW,
    e.Windspeed,
    b.Percent_Bleached
FROM Sample_Event_tbl AS se
JOIN Site_Info_tbl AS si
  ON si.Site_ID = se.Site_ID
JOIN Environmental_tbl AS e
  ON e.Sample_ID = se.Sample_ID
JOIN Bleaching_tbl AS b
  ON b.Sample_ID = se.Sample_ID
WHERE si.Data_Source = 2
  AND se.Date_Year BETWEEN 2005 AND 2016
  AND b.Percent_Bleached IS NOT NULL
ORDER BY se.Date_Year, se.Date_Month, se.Date_Day, se.Site_ID, se.Sample_ID;
