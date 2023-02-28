DELETE FROM
    sessions AS a
WHERE
    a.expired < CURRENT_TIMESTAMP - interval '1 hour'
;