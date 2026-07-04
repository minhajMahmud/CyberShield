# Viva / Project Defense Preparation
## CyberShield – Secure Digital Security Platform

## A. Architecture & Design Questions

**Q1. Why did you combine four separate security tools into one platform
instead of building four separate projects?**
> A single account, single audit trail, and shared user-management layer
> mirror how real security platforms work (e.g. an identity/security
> suite), and it forces the design to handle cross-cutting concerns —
> authentication, authorisation, logging — consistently rather than
> duplicating them four times.

**Q2. Why Flask instead of Django?**
> Flask is a micro-framework: it gives routing and templating but leaves
> architecture decisions to us, which let us design the blueprint /
> service-layer split (`routes/` calling into `utils/`) explicitly and
> explain every piece rather than relying on framework-generated
> boilerplate.

**Q3. Why MySQL and not a NoSQL database?**
> The data is inherently relational — users own files, signatures, OTPs,
> and log entries with clear foreign-key relationships and the need for
> referential integrity (e.g. a file must belong to an existing user).
> MySQL with InnoDB gives us ACID transactions and foreign-key
> constraints, which are the right guarantees for security-relevant data.

**Q4. Walk me through the folder structure.**
> `models/` holds one SQLAlchemy class per table; `routes/` holds one
> Flask blueprint per functional module; `utils/` holds the pure
> cryptography/logic functions with no Flask dependencies, so they are
> independently unit-testable; `templates/` and `static/` hold the
> presentation layer.

## B. Cryptography Questions

**Q5. Why AES-256-GCM specifically, and not AES-CBC?**
> GCM is an *authenticated* encryption mode: it produces a ciphertext plus
> an authentication tag in one step, so decryption both decrypts and
> verifies integrity — any single-bit change to the ciphertext causes
> decryption to fail loudly. CBC alone gives confidentiality but no
> integrity, and is vulnerable to padding-oracle attacks unless paired
> with a separate MAC (encrypt-then-MAC), which GCM already does for us.

**Q6. What is "envelope encryption" and why use it here?**
> Each file gets its own randomly generated 256-bit Data Encryption Key
> (DEK). The DEK encrypts the file; the DEK itself is then encrypted
> ("wrapped") by a single master key that lives only in an environment
> variable, never in the database. This means a database leak alone
> reveals nothing usable — an attacker also needs the master key and the
> ciphertext on disk. It also means we can rotate the master key without
> re-encrypting every file — just re-wrap the DEKs.

**Q7. Why RSA-2048 and SHA-256 for digital signatures?**
> RSA-2048 is the current minimum recommended key size for RSA to resist
> brute-force factoring with today's computing power. We hash the
> document with SHA-256 first (fixed-size 256-bit digest) and sign the
> hash rather than the raw document — this is both far faster and is what
> every real signature scheme (X.509, PGP, code signing) does. We use
> RSA-PSS padding rather than the older PKCS#1 v1.5, since PSS has a
> stronger security proof.

**Q8. How does your app detect a tampered document?**
> Verification recomputes the SHA-256 hash of the *presented* document and
> checks the stored signature against that hash using the public key. If
> even one byte of the document changed, the recomputed hash differs from
> the one that was originally signed, and RSA-PSS verification fails
> deterministically — we surface this as `status = tampered`.

**Q9. Why bcrypt for password storage instead of SHA-256?**
> SHA-256 is fast, which is exactly the wrong property for password
> hashing — it makes brute-force/dictionary attacks cheap. bcrypt is
> deliberately slow and includes a per-password random salt plus a
> tunable work factor, making offline cracking far more expensive per
> guess.

**Q10. How does TOTP (the QR-code 2FA) actually work without any network
call at verification time?**
> Both the server and the authenticator app share the same secret (set up
> once, via the QR code). TOTP derives a 6-digit code from `HMAC(secret,
> current_30-second_time_window)`. Because both sides compute
> independently from the same secret and the same clock, no network
> round-trip is needed to verify — the server just recomputes the same
> code for the current time window and compares.

## C. Security Questions

**Q11. How do you prevent SQL injection?**
> All database access goes through SQLAlchemy's ORM query API, which
> parameterises every value — we never string-concatenate user input into
> a SQL statement.

**Q12. How do you prevent XSS?**
> Jinja2 templates auto-escape all variables by default; we never use the
> `|safe` filter on anything derived from user input.

**Q13. How is CSRF handled?**
> Flask-WTF issues a per-session CSRF token embedded in every form; the
> server rejects any state-changing POST request without a valid matching
> token.

**Q14. What happens if someone brute-forces the login form?**
> `failed_attempts` increments on every wrong password; after a threshold
> the account is temporarily locked (`locked_until`), and every attempt
> — successful or not — is written to `Activity_Log` for later review.

**Q15. Where are the encryption keys stored, and why not in the database?**
> The AES master key lives only in an environment variable
> (`AES_MASTER_KEY`), never in the database or source code, following the
> principle that encrypted data and the key that protects it should never
> sit in the same place. RSA private keys are stored encrypted-at-rest
> rather than in plaintext.

## D. Project Management / Testing Questions

**Q16. How did you test this project?**
> A pytest suite (17 automated tests) covers unit-level crypto correctness
> (encrypt/decrypt round-trips, tamper detection, signature verification),
> plus integration tests through Flask's test client (register → login →
> upload → download, access-control checks on admin routes).

**Q17. What would you improve given more time?**
> Add WebAuthn/FIDO2 hardware-key support alongside TOTP, move file
> storage to S3-compatible object storage with server-side encryption,
> add per-file granular sharing/permissions, and add rate-limiting at the
> reverse-proxy layer in addition to the application layer.

**Q18. What was the hardest part of the project?**
> Getting the envelope-encryption key hierarchy right — making sure the
> master key never touches the database and that a corrupted or tampered
> ciphertext fails safely (raises an error) instead of silently returning
> garbage data.
