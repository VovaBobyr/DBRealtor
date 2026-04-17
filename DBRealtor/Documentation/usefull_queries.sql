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


SELECT  obj_number ,COUNT(*) FROM projekty
GROUP BY obj_number
HAVING COUNT(*) > 1

SELECT * FROM projekty_items WHERE obj_number ='2556641628'
SELECT * FROM projekty WHERE obj_number = '9541'

SELECT * FROM dbrealtor.projekty WHERE obj_number='9530'

CREATE TABLE projekty_items_copy AS SELECT * FROM projekty_items

SELECT uzitna_plocha,  CONVERT('55', SIGNED INTEGER)
FROM projekty_items
WHERE CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65

SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)
CONVERT(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)), INTEGER)

SELECT title, cena, poznamka_k_cene, region, subregion, podlazi, uzitna_plocha, link  FROM projekty_items WHERE
cena < 6000000 AND
((title LIKE '%2+kk%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
(title LIKE '%2+1%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
title LIKE '%3+kk%' OR title LIKE '%3+kk%' OR
title LIKE '%4+kk%' OR title LIKE '%4+1%')
AND (region LIKE '%Praha%' OR subregion LIKE '%Praha%')
ORDER BY cena

SELECT title, cena, poznamka_k_cene, date_open, date_close, region, subregion, podlazi, uzitna_plocha, link  FROM byty_prodej WHERE
cena < 5000000 AND
((title LIKE '%2+kk%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
(title LIKE '%2+1%' AND CONVERT(REPLACE(SUBSTRING(uzitna_plocha, 1, LOCATE(' m2', uzitna_plocha)),' ', ''), UNSIGNED INTEGER) > 65) OR
title LIKE '%3+kk%' OR title LIKE '%3+kk%' OR
title LIKE '%4+kk%' OR title LIKE '%4+1%')
AND (region LIKE '%Praha%' OR subregion LIKE '%Praha%')
ORDER BY cena

SELECT * FROM dataloadlog WHERE type = 'byty_prodej'
ORDER BY date_start desc