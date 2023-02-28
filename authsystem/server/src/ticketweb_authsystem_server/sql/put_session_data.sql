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
;
