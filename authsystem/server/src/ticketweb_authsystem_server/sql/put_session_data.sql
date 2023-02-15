INSERT INTO
   sessions
     (
      session_id,
      expired,
      net_id,
      real_name,
      email
     )
VALUES
     (%s, CURRENT_TIMESTAMP + INTERVAL '1 min' * %s, %s, %s,%s)
ON CONFLICT
     (
      session_id 
     )
DO UPDATE SET
    net_id = excluded.net_id,
    expired = excluded.expired,
    real_name = excluded.real_name,
    email = excluded.email
;
