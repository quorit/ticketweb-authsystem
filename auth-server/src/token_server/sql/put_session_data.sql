INSERT INTO
   sessions
     (
      session_id,
      user_dn,
      expired
     )
VALUES
     (%s, %s,CURRENT_TIMESTAMP + INTERVAL '1 min' * %s)
ON CONFLICT
     (
      session_id 
     )
DO UPDATE SET
    user_dn = excluded.user_dn,
    expired = excluded.expired
;
