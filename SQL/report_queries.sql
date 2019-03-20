SELECT DATE(date_start) AS date_run, SUM(inserted_count), type FROM dataloadlog
WHERE TYPE='byty_prodej'
GROUP BY date_run, TYPE
UNION ALL 
SELECT DATE(date_start) AS date_run, SUM(inserted_count), type FROM dataloadlog
WHERE TYPE='byty_pronajem'
GROUP BY date_run, type
SELECT * FROM dataloadlog ORDER BY id desc
--WHERE DATE(date_start) = '2019-03-17' AND TYPE = 'byty_prodej'

ORDER BY date_start DESC
SELECT *  FROM dataloadlog
delete FROM dataloadlog WHERE id IN (42)
SELECT COUNT(*) FROM byty_prodej
SELECT * FROM byty_prodej LIMIT 30
UPDATE byty_prodej
SET STATUS = 'O', date_close = NULL
WHERE date_close > '2019-03-15 13:46:00'
-- Calculate count of updated and inserted rows
SELECT COUNT(*) FROM byty_prodej 
WHERE date_update > '2019-03-18 11:04:00'
SELECT COUNT(*) FROM byty_prodej 
WHERE date_open > '2019-03-18 11:04:00'
-- Caclulate how long items are actuall !!!
SELECT COUNT((DATE(date_update) - DATE(date_open))) AS Count_Diff, (DATE(date_update) - DATE(date_open)) AS diff FROM byty_prodej 
WHERE STATUS != 'C'
GROUP BY diff
ORDER BY diff

SELECT COUNT((DATE(date_update) - DATE(date_open))) AS Count_Diff, (DATE(date_update) - DATE(date_open)) AS diff FROM byty_pronajem 
WHERE STATUS != 'C'
GROUP BY diff
ORDER BY diff

SELECT * FROM dataloadlog WHERE TYPE = 'byty_prodej'
DELETE FROM  dataloadlog WHERE id=44
SELECT * FROM dbrealtor.byty_prodej ORDER BY id DESC LIMIT 10 

INSERT INTO dbrealtor.byty_pronajem
(id_load,title,obj_number,date_open,status,cena,celkova_cena,poznamka_k_cene,puvodni_cena,description,link,region,subregion,aktualizace,id_ext,stavba,stav_objektu,vlastnictvi,
umisteni_objektu,podlazi,uzitna_plocha,terasa,sklep,voda,topeni,plyn,odpad,telekomunikace,elektrina,doprava,komunikace,vybaveni,kontakt) 
VALUES('22','','4235759196','2019-03-19 11:50:16','','4700','4 700 Kč za měsíc','+ služby 1520, kauce 6220, + adm. poplatek 4700','',
'Pronájem bytové jednotky 1 + 1, ul. Rudé armády 2974/4e, Karviná-Hranice k dlouhodobému pronájmu s možností trvalého pobytu. Nabízíme malý byt po kompletní rekonstrukci v žádané lokalitě, v 1. patře panelového domu. Zastávky MHD před domem, obchodní centrum v místě. Doporučujeme nezávaznou prohlídku. K pronájmu od 1.4.2019 Ceny uvedené u položek Kauce/Jistota, Administrační poplatek a služby - jsou orientační. Nájemné se hradí v daném měsíci. Kauce/Jistota je ve výši jednonásobku nájemného + služeb.',
'https://www.sreality.cz/detail/pronajem/byt/1+1/karvina-cast-obce-hranice-ulice-rude-armady/4235759196','Karviná','','Dnes','F1929011','Panelová','Velmi dobrý','Osobní','Sídliště',
'2. podlaží z celkem 4','37 m2','','','Dálkový vodovod','','','','','230V','','','','http://www.residomo.cz')


update dbrealtor.byty_pronajem set date_close="2019-03-19 12:11:05", status="C" 

SELECT * FROM dbrealtor.byty_prodej
where (date_update < "2019-03-20 10:00:06" AND STATUS !="C") OR (date_open < "2019-03-20 10:00:06" AND date_update IS NULL AND STATUS !="C")
SELECT * FROM dbrealtor.byty_prodej WHERE id_load = 45
AND date_update IS NOT NULL OR date_update IS NULL


--update dbrealtor.byty_pronajem 
set date_close="2019-03-19 12:29:42", status="C" 
SELECT * FROM dbrealtor.byty_pronajem
WHERE (date_update < "2019-03-19 12:28:54" AND STATUS !="C") OR (date_open < "2019-03-19 12:28:54" AND date_update IS NULL AND STATUS !="C")

update dbrealtor.byty_pronajem set date_close="2019-03-19 12:32:06", status="C" 
SELECT * FROM dbrealtor.byty_pronajem
where (date_update < "2019-03-19 12:31:48" OR date_open < "2019-03-19 12:31:48") AND STATUS !="C"

OR (date_open < "2019-03-19 12:31:48" AND date_update IS NULL AND STATUS !="C")

SELECT * FROM dbrealtor.byty_pronajem ORDER BY id DESC LIMIT 10 
WHERE STATUS != 'C'

--update dbrealtor.byty_pronajem set date_close="2019-03-19 12:32:06", status="C"
SELECT * FROM dbrealtor.byty_pronajem 
where (date_update < "2019-03-19 13:41:02" AND STATUS !="C") OR (date_open < "2019-03-19 13:41:02" AND date_update IS NULL AND STATUS !="C")














