byty_pronajemSELECT * from dbrealtor.byty_pronajem ORDER BY date_close desc
set date_close="2019-03-14 09:34:03", status="C"

SELECT * FROM dbrealtor.byty_pronajem
where date_update < "2019-03-14 09:33:45" OR (date_open < "2019-03-14 09:33:45" AND date_update IS NULL)

update dbrealtor.byty_pronajem set date_close="2019-03-14 10:30:29", status="C"
SELECT * FROM dbrealtor.byty_pronajem
where date_update < "2019-03-14 10:30:01" OR (date_open < "2019-03-14 10:30:01" AND date_update IS NULL)