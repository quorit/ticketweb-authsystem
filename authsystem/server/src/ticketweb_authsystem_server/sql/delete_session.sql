UPDATE sessions SET
    expired = CURRENT_TIMESTAMP
WHERE
    session_id = %s
;