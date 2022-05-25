SELECT a FROM (SELECT * FROM x);
SELECT "_q_0".a AS a FROM (SELECT x.a AS a FROM x) AS "_q_0";

SELECT 1 FROM (SELECT * FROM x) WHERE b = 2;
SELECT 1 AS "_col_0" FROM (SELECT x.b AS b FROM x) AS "_q_0" WHERE "_q_0".b = 2;

SELECT a FROM x JOIN (SELECT b, c FROM y) AS z ON x.b = z.b;
SELECT x.a AS a FROM x JOIN (SELECT y.b AS b FROM y) AS z ON x.b = z.b;

SELECT x1.a FROM (SELECT * FROM x) AS x1, (SELECT * FROM x) AS x2;
SELECT x1.a AS a FROM (SELECT x.a AS a FROM x) AS x1, (SELECT 1 AS "_" FROM x) AS x2;

SELECT x1.a FROM (SELECT * FROM x) AS x1, (SELECT * FROM x) AS x2;
SELECT x1.a AS a FROM (SELECT x.a AS a FROM x) AS x1, (SELECT 1 AS "_" FROM x) AS x2;

SELECT a FROM (SELECT DISTINCT a, b FROM x);
SELECT "_q_0".a AS a FROM (SELECT DISTINCT x.a AS a, x.b AS b FROM x) AS "_q_0";

SELECT a FROM (SELECT a, b FROM x UNION ALL SELECT a, b FROM x);
SELECT "_q_0".a AS a FROM (SELECT x.a AS a FROM x UNION ALL SELECT x.a AS a FROM x) AS "_q_0";

SELECT a FROM (SELECT a, b FROM x UNION SELECT a, b FROM x);
SELECT "_q_0".a AS a FROM (SELECT x.a AS a, x.b AS b FROM x UNION SELECT x.a AS a, x.b AS b FROM x) AS "_q_0";

WITH y AS (SELECT * FROM x) SELECT a FROM y;
WITH y AS (SELECT x.a AS a FROM x) SELECT y.a AS a FROM y;

WITH z AS (SELECT * FROM x), q AS (SELECT b FROM z) SELECT b FROM q;
WITH z AS (SELECT x.b AS b FROM x), q AS (SELECT z.b AS b FROM z) SELECT q.b AS b FROM q;

WITH z AS (SELECT * FROM x) SELECT a FROM z UNION SELECT a FROM z;
WITH z AS (SELECT x.a AS a FROM x) SELECT z.a AS a FROM z UNION SELECT z.a AS a FROM z;
