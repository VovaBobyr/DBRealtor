ALTER DATABASE dbrealtor CHARACTER SET utf8 COLLATE utf8_unicode_ci;
select * from dbrealtor.byty limit 10  where link like '%442609244%'
select * FROM information_schema.SCHEMATA S WHERE schema_name = "dbrealtor";
ALTER SCHEMA dbrealtor DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci; 
ALTER DATABASE dbrealtor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE dbrealtor.byty CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

update dbrealtor.byty date_open='O';
where typ_bytu is null

SELECT link, obj_number FROM dbrealtor.byty limit 20

SET SQL_SAFE_UPDATES = 0;
update dbrealtor.byty set obj_number=442609244 WHERE link="https://www.sreality.cz/detail/prodej/byt/2+kk/praha-cast-obce-modrany-ulice-ceskoslovenskeho-exilu/442609244"

select count(*) from dbrealtor.byty where obj_number is NULL
update dbrealtor.byty set date_update="2019-03-06 15:20:27", status="U" where obj_number="1152360028"
SELECT * FROM dbrealtor.byty WHERE link like '%1152360028%'
update dbrealtor.byty set date_update="2019-03-06 15:07:09" where obj_number="442609244" and status="U"
update dbrealtor.byty set date_update="2019-03-06 15:07:09", status="U"  where obj_number="442609244"

update dbrealtor.byty set date_update="2019-03-06 15:17:34", status="U" where obj_number="1152360028"

SELECT id, obj_number, link FROM byty WHERE id=18212
SELECT COUNT(*) FROM byty WHERE obj_number IS NULL -- 9874

UPDATE byty
SET obj_number= SUBSTRING(link, CHAR_LENGTH(link) - LOCATE('/', REVERSE(link)) + 2, CHAR_LENGTH(link))
FROM byty LIMIT 10

SELECT date_open, date_update, date_close, status status FROM byty WHERE obj_number='1271963228'
update dbrealtor.byty set date_update="2019-03-06 16:10:08", status="U" where obj_number="2024227164"