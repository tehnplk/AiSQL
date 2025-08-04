SELECT v.village_id,
       v.village_moo,
       v.village_name,
       count(p.person_id) AS `population`
FROM person p
JOIN house h ON p.house_id = h.house_id
JOIN village v ON h.village_id = v.village_id
WHERE (p.person_discharge_id IS NULL
       OR p.person_discharge_id = 9)
GROUP BY v.village_id,
         v.village_moo,
         v.village_name
ORDER BY v.village_id