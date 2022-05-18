UPDATE
    sessions
SET
    expired = CURRENT_TIMESTAMP + INTERVAL '1 min' * %s
WHERE
    session_id = %s
;
