SELECT * FROM
(SELECT p.date_open,p.date_update,p.date_close,DATEDIFF(CURDATE(),DATE(p.date_open)) as diff, p.subregion, p.uzitna_plocha, ROUND(cena/SUBSTRING(p.uzitna_plocha, 1, 2), 0) AS kpi,
p.* FROM dbrealtor.byty_prodej AS p WHERE region LIKE '%Praha%'
AND (title LIKE '%3+kk%' OR title LIKE '%4+kk%' OR title LIKE '%3+1%' OR title LIKE '%4+1%') AND cena !=0
AND vlastnictvi !='Družstevní' AND cena < 5000000 AND date_close IS NULL)

