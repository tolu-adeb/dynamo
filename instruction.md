There is an Apache-style access log at `/app/access.log`. Parse it and write a
JSON summary report to `/app/report.json`.

Success criteria (checked exactly by the verifier):

1. `/app/report.json` exists, is valid JSON, and is a single object containing
   exactly these three keys -- no more, no fewer:
   - `total_requests` (integer)
   - `unique_ips` (integer)
   - `top_path` (string)
2. `total_requests` equals the number of non-empty lines in `/app/access.log`.
3. `unique_ips` equals the number of distinct client IP addresses in the log
   (the first whitespace-delimited token on each line).
4. `top_path` equals the request path requested the most times. The path is
   the second token inside the quoted request line -- e.g. for
   `"GET /index.html HTTP/1.1"` the path is `/index.html`.
