# FSCT 8561 – Lab 5 Answers
**Name:** Billy Zandan

---

## Part A — Understanding HTTP

### A1. Check Your Understanding
**Q: What is the difference between `response.status_code` and `len(response.content)`?**

`response.status_code` is a 3-digit number the server sends to describe _how_ the request went (e.g., `200` = OK, `404` = not found). `len(response.content)` is the size of the actual data the server sent back, measured in bytes. One tells you the result of the request; the other tells you how much content arrived.

---

### A2. Try It – String Slicing
**Q: What does `[:50]` do?**

It returns only the first 50 characters of the string, instead of the whole thing. Slicing with `[:n]` starts at index 0 and stops just before index `n`.

---

### Practice A – Search Term Change
**Q: Which part of the request changed when searching "banana"? Did the status code change?**

Only the value of the `q` query parameter changed (`?q=banana` instead of `?q=apple`). The status code stayed `200` in both cases because the server still processed the request successfully, even if the results were different.

---

### Practice B – GET vs POST
**Q: Compare GET and POST results. Why doesn't a `405` indicate a vulnerability?**

`GET /rest/products/search?q=apple` returned `200` with JSON product data. `POST` to the same path returned `405 Method Not Allowed`. A `405` just means the server doesn't accept that HTTP method on that path — it's the server working correctly and enforcing rules, not a security flaw.

---

## Part B — Python Building Blocks

### Practice C – Adding "lemon" to the list
**Q: How many times does the loop run?**

Four times — once for each item: `apple`, `banana`, `orange`, and `lemon`.

---

### Practice D – Adding `content_type` to the dictionary
```python
observation["content_type"] = r.headers.get("Content-Type")
print(observation["content_type"])
```
This adds the `Content-Type` header value (e.g., `application/json; charset=utf-8`) as a named field in the dictionary.

---

### Practice E – Adding `response_length` + explanation
```python
records.append({
    "input": term,
    "status_code": result.status_code,
    "response_length": len(result.content)
})
```
**Why is a list of dictionaries helpful?** Each dictionary is a self-labeled record. When you loop over the list to print or export a report, every field has a name, so the output is easy to read and you don't mix up column order.

---

### Practice F – `get_status("banana")` + explanation
```python
print(get_status("banana"))
```
`search_word` is the **parameter** of the function — a local placeholder that takes whatever value you pass in when you call the function. Inside the function, `search_word` holds `"banana"`, so the request uses `?q=banana`. It doesn't exist outside the function.

---

### Practice G – Why use timeout and exception handling?
A timeout stops Python from waiting forever if the server is slow or unreachable — without it, the script could hang indefinitely. `requests.RequestException` catches any network-level failure (connection refused, DNS failure, timeout) so the script reports the problem cleanly instead of crashing with an unhandled error.

---

## Part C — Security Indicators

### Practice H – HTML Reflection and XSS
**Q: Does `<u>fsct8561-test</u>` appearing in the response prove XSS?**

No. The Juice Shop search API returns results as JSON, so the tag appears as plain text data inside a JSON string — the browser never interprets it as HTML. For XSS to occur, the browser must execute the input as code. Reflection alone is not sufficient; you must verify that the response is rendered as HTML in an unsafe context without escaping.

---

### Practice I – SQL Probe Comparison
**Q: Explain the observation. Why is a baseline comparison more informative?**

The normal input (`apple`) returns `200` with product data. The probe (`'`) may return a different status or a longer/shorter body. Without a baseline you can't tell whether the different response is caused by the probe or is just normal variation. Comparing against a known-good request shows whether the server is behaving differently in response to the suspicious input.

---

### Practice J – Additional DB Error Phrases + Explanation
Two additional phrases a detector might check:
- `"syntax error"` — common in SQLite and other databases when a query is malformed.
- `"unclosed quotation mark"` — a specific SQL Server / PostgreSQL error triggered by an unbalanced quote.

**Why doesn't a matching phrase confirm SQL injection?** The phrase could appear for many reasons (e.g., the word "error" in a product description, or a generic validation message). Confirming SQLi requires verifying that attacker-controlled input is actually inserted into and executed by a database query — something a simple text match can't establish.

---

### Practice K – Server Header
```python
print(response.headers.get("Server"))
```
The `Server` header may reveal the server software and version (e.g., `nginx/1.18.0`). This is information disclosure — it could help an attacker target known vulnerabilities for that version. However, it is **not automatically critical** because many servers are patched regardless of what the header says, and the header alone gives no exploitation capability.

---

### Practice L – Deduplication with a `set`
**Q: Why does the list contain only two alerts?**

The `seen` set tracks which messages have already been added. When `"Missing CSP"` appears a second time, it's already in `seen`, so the `if` condition is `False` and it's skipped. Only two _unique_ messages are added to `alerts`.

In the final detector, a finding should be considered a duplicate if its **category + endpoint + observation** combination already exists — this prevents the same issue from appearing multiple times in the report.

---

### Practice M – CSV File Structure
`practice_records.csv` has **two column headings**: `endpoint` and `status`, and **two data rows**:

| endpoint | status |
|---|---|
| / | 200 |
| /example | 404 |

CSV is useful for the final report because it can be opened in Excel or any spreadsheet tool, is easy to share, and can be parsed programmatically, making scanner output reproducible and easy to review.

---

## Task 3 — Server and Configuration Analysis

### Headers Present and Missing

Based on the actual response from the local Juice Shop homepage (`/`):

* **Present Headers:**
  * `Content-Type: text/html; charset=UTF-8` (specifies the MIME type and character encoding)
  * `X-Content-Type-Options: nosniff` (security header preventing browsers from MIME-sniffing)
  * `X-Frame-Options: SAMEORIGIN` (prevents clickjacking by allowing framing only by the same origin)
  * `Access-Control-Allow-Origin: *` (CORS header allowing cross-origin requests from any origin)
  * `Feature-Policy: payment 'self'` (restricts browser features like payment APIs)
  * `X-Recruiting: /#/jobs` (custom Easter egg header)
  * Standard HTTP headers: `Date`, `Connection`, `Keep-Alive`, `Cache-Control`, `ETag`, `Vary`, `Content-Encoding`, `Transfer-Encoding`.

* **Missing Headers:**
  * `Content-Security-Policy` (CSP) — absent; the browser lacks directives on which script/style/media origins are trusted.
  * `Strict-Transport-Security` (HSTS) — absent (though expected since this is an HTTP-only local test).
  * `Server` and `X-Powered-By` — absent / stripped.

### Server Header
Juice Shop may return a `Server: nginx` or similar header. This is **informational** — it reveals the web server but doesn't directly enable an attack.

### HTTPS / TLS Assessment
You cannot meaningfully assess TLS on a `http://localhost` endpoint because there is no TLS in use. In a real HTTPS deployment you would examine:
- The TLS version (TLS 1.2 minimum; TLS 1.3 preferred).
- The cipher suites offered (reject weak ciphers like RC4, 3DES).
- Certificate validity, expiry, and chain of trust.
- Whether HSTS (`Strict-Transport-Security`) is present with a sufficient `max-age`.
- Whether HTTP redirects to HTTPS (no mixed content).

### Missing Header ≠ Exploitable Vulnerability
A missing header reduces browser-level defence in depth, but exploitation still requires an attack vector. For example, missing CSP only matters if an XSS injection point exists _and_ the response is rendered as HTML in a browser. Without that, the missing header has no practical impact.

---

## Task 5 — Reflection and Security Analysis (~370 words)

The HTTP scanner collected factual observations: endpoint paths, HTTP methods, status codes, response sizes, content types, and the `Server` header. It made no claims about whether the application was vulnerable — it simply recorded what the server returned. The vulnerability detector then applied pattern checks: it looked for reflected input, compared probe responses against a normal baseline, and noted absent security headers.

What the detector flagged as indicators included: input reflection in the search endpoint, a possible anomalous status code when a SQL syntax probe was submitted, and missing security headers on the homepage. Importantly, none of these alone confirm a vulnerability. Reflection inside a JSON body is not XSS. A `500` status on a probe suggests something unusual happened server-side, but it does not prove that an attacker can extract data. Missing headers reduce browser-enforced defences but require an actual attack path to matter.

If I were the security lead for Juice Shop, I would prioritise investigating the SQL injection indicator first. A `500` response to a simple quote character probe is a strong sign that the input is being interpolated directly into a database query. Unlike a missing header (which is a configuration fix), an active SQLi vulnerability could expose the entire database. I would follow up with manual testing and code review to confirm whether the query is truly injectable.

This lab extends Lab 4's passive packet analysis by moving from observing traffic to actively sending crafted requests. Packet capture shows *what bytes moved across the wire*, but not application-level logic. HTTP-layer testing reveals how the application processes input, which headers it sets, and whether error conditions expose internal information.

If the application used HTTPS, a packet capture would show only encrypted ciphertext — an attacker could see that a connection occurred and roughly how much data moved, but not the content. A Python HTTP client making an authorized request, however, receives the full decrypted response and can inspect headers, body content, and status codes. This is why authorized application-layer testing provides richer security insights than passive network capture on an encrypted channel.

Finally, automated findings must always be manually verified. Tools produce false positives and false negatives. Reporting an unverified automated match as a confirmed vulnerability could misdirect remediation effort and damage trust in the security report.

---

## Deliverables Summary

| File | Description |
|---|---|
| `http_scanner.py` | Task 1 – HTTP observation collector |
| `vulnerability_detector.py` | Task 2 – Indicator checker with deduplication |
| `http_scan_results.csv` | Generated by running `http_scanner.py` |
| `vulnerability_findings.csv` | Generated by running `vulnerability_detector.py` |
| `Lab5_Answers.md` | This file – written answers |

### How to run the scripts
```powershell
# Make sure Docker Desktop is running and Juice Shop is up:
docker run --rm -d --name fsct8561-juice -p 127.0.0.1:3000:3000 bkimminich/juice-shop

# Install dependency (once):
pip install requests

# Run the scanner:
python http_scanner.py

# Run the detector:
python vulnerability_detector.py
```

