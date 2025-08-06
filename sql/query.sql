SELECT p.pname AS `คำนำหน้าชื่อ`,
       p.fname AS `ชื่อ`,
       p.lname AS `นามสกุล`,
       o.vstdate AS `วันที่วินิจฉัย`,
       i.name AS `ชื่อโรค`,
       od.icd10 AS `รหัสโรค`
FROM person p
JOIN ovst o ON p.patient_hn = o.hn
JOIN ovstdiag od ON o.vn = od.vn
JOIN icd101 i ON od.icd10 = i.code
WHERE od.icd10 = 'J00'
    AND YEAR(o.vstdate) = 2024