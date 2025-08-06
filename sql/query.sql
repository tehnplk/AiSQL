SELECT person_id,
       pname AS `คำนำหน้า`,
       fname AS `ชื่อ`,
       lname AS `นามสกุล`,
       CASE
           WHEN sex = '1' THEN 'ชาย'
           WHEN sex = '2' THEN 'หญิง'
           ELSE NULL
       END AS `เพศ`,
       timestampdiff(YEAR, person.birthdate, curdate()) AS `อายุ`
FROM person