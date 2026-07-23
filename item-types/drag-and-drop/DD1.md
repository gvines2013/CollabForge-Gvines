# Drag-and-drop item · DD1

**Item D5 · Identity — SAML SSO**

Drag each SAML SSO step into the correct order of the login sequence (1 → 5).
Order
Step / content
Step 1
SP generates AuthnRequest → HTTP 302 redirect to the IdP
Step 2
User authenticates at the IdP (password / MFA / Kerberos)
Step 3
IdP returns a signed SAML assertion (subject, conditions, audience)
Step 4
SP validates signature, timestamps (NotBefore/NotOnOrAfter) and audience
Step 5
Session established; OAuth access / refresh tokens issued
Answer key — correct order shown.

**Source:** https://www.cisco.com/c/en/us/support/docs/unified-communications/unified-communications-manager-callmanager/211302-Configure-Single-Sign-On-using-CUCM-and.html

_Related design items: D5_
