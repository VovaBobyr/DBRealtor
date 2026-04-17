SELECT * FROM dataloadlog
SELECT MAX(id) FROM dataloadlog
DELETE FROM dataloadlog WHERE id = 6

UPDATE dataloadlog
SET STATUS='Closed', items_count=8975, pages_count=449, skipped_count=8835, failed_count=0, closed_count=1151
WHERE id=7

SELECT * FROM byty_pronajem WHERE STATUS = 'C'
ORDER BY date_close

INSERT INTO dbrealtor.dataloadlog (type, date_start, status) VALUES(\\'byty_prodej\\', \\'2019-03-15 09:50:08\\', \\'Open\\', 18411, 921)