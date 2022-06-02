SELECT 
    a.expired,
    a.user_dn 
FROM
    sessions AS a
WHERE
    a.session_id = %s
;