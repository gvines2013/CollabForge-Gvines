# Matrix item · MX4

**Item D4 / D12 · Local Gateway — Registration-based vs Certificate-based**

Multiple-answer matrix. For each characteristic (row), select the Local Gateway trunk model(s) (column) it applies to. A row may apply to one or both models.
Options
Registration-based LGW
Certificate-based LGW
Authenticates via SIP digest registration (username / password)
✓

Authenticates via mutual TLS with a CA-signed FQDN certificate

✓
Scales to ~250 concurrent calls
✓

Scales to ~2,000 concurrent calls (OTT)

✓
Requires a claimed/verified domain + public DNS (A/SRV) FQDN

✓
Works behind NAT without a public certificate
✓

Runs on CUBE / IOS-XE as the Local Gateway
✓
✓

**Source:** https://help.webex.com/en-us/article/t9xctu/Get-started-with-Local-Gateway

_Related design items: D4, D12_
