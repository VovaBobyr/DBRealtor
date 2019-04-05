SELECT * FROM
(SELECT p.date_open,p.date_update,p.date_close,DATEDIFF(CURDATE(),DATE(p.date_open)) as diff, p.subregion, p.uzitna_plocha, ROUND(cena/SUBSTRING(p.uzitna_plocha, 1, 2), 0) AS kpi,
p.* FROM dbrealtor.byty_prodej AS p WHERE region LIKE '%Praha%'
AND (title LIKE '%3+kk%' OR title LIKE '%4+kk%' OR title LIKE '%3+1%' OR title LIKE '%4+1%') AND cena !=0
AND vlastnictvi !='Družstevní' AND cena < 5000000 AND date_close IS NULL)

-- Selection from projects
-- 3,4 or 2 with condition squ
SELECT title, cena, poznamka_k_cene, region, subregion, podlazi, uzitna_plocha  FROM projekty_items WHERE
cena < 6000000 AND
((title LIKE '%2+kk%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
(title LIKE '%2+1%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
title LIKE '%3+kk%' OR title LIKE '%3+kk%' OR
title LIKE '%4+kk%' OR title LIKE '%4+1%')
ORDER BY cena
