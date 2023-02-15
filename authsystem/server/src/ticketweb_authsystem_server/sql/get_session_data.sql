SELECT 
    a.expired,
    a.net_id,
    a.real_name,
    a.email
FROM
    sessions AS a
WHERE
    a.session_id = %s
;