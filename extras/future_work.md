# Future Work

Running list of future directions for the dissertation. Many of these came from design discussions where an idea was sound but out of scope for a two-month PoC. Naming them shows understanding of the field's frontier. Polish into prose later.

---

## 1. Additional signals
- Implement the designed-but-not-built signals: session timing (duration and time-of-day patterns), mouse movement dynamics, scroll behaviour, and navigation flow.
- These are all post-login behavioural signals that work regardless of login method, strengthening the continuous-authentication case.
- Mobile-only signals for a future mobile version: touch gestures (swipe/tap pressure) and device handling (accelerometer/gyroscope orientation).
- Free-text keystroke dynamics (analysing typing rhythm on any text typed during a session, not just a fixed password). Harder than fixed-text but would recover the keystroke signal even under passwordless login.

---

## 2. Stronger evaluation
- Extend the keystroke evaluation from 10 users to all 51 CMU users for a stronger headline number.
- Larger and more diverse volunteer pool for the live signals to reduce self-testing bias.
- Use real IP and geolocation instead of simulated values.
- Derive thresholds empirically from data rather than choosing them as design parameters.
- More extensive adversarial testing (mimicry attacks, replay, etc.).
- Formal metrics (FAR, FRR, EER) at scale — deliberately simplified in this PoC to counts of correct/incorrect decisions, but a fuller study could compute these properly.

---

## 3. True decentralisation
- Deploy the smart contract to a distributed test network (e.g. a public testnet such as Sepolia, which uses free test ETH) or a multi-node private/permissioned chain, to move beyond the single-node Ganache simulation and genuinely demonstrate decentralisation.
- A production/enterprise deployment (e.g. for a bank) would use a private or permissioned blockchain such as Hyperledger Fabric, avoiding public-network per-transaction fees while keeping immutability and distributed integrity. The main real-world costs would be integration, auditing, and compliance, not the blockchain itself.

---

## 4. Stronger local data security
- Encrypt behavioural data at rest (symmetric encryption). Simple password-derived key (via a key derivation function such as PBKDF2/bcrypt/scrypt/Argon2 with a per-user salt) as the PoC-level version.
- Store the encryption key in the OS secure store (macOS Keychain / secure enclave, or platform equivalent) so it is guarded by hardware and never held in the app or files. An attacker with just the password and database file still could not get the key.
- Per-user keys and partial decryption: don't decrypt the whole database at once; encrypt each user's patterns with a different key so a single compromise has a limited blast radius.
- Template protection techniques (e.g. fuzzy extractors / biohashing, as in Liao 2024) so that stored behavioural data cannot be reversed even if the store is breached — addresses the irreversibility problem of biometric data.
- Note the honest boundary: no local storage is perfectly secure against an attacker who has fully compromised the machine. The goal is to raise cost and narrow the window against realistic threats.

---

## 5. Defending the integrity mechanism further
- Protect the blockchain signing key in hardware (HSM / secure enclave) so an attacker who reverse-engineers the app still cannot submit valid hashes for tampered data.
- Smart-contract-based write authorisation so only specific verified identities can submit hashes, not anyone who can run the app's code.
- Cumulative drift check against the immutable original enrolment anchor: even if an attacker updates the working pattern and its hash, the original enrolment hash is permanent, so impossibly large drift from the original baseline can be detected. Helps catch slow-poisoning attacks.

---

## 6. Adaptive learning improvements
- The system already does online adaptive learning (drift detection + controlled pattern updates, only learning from vote-passed logins to prevent poisoning). This is the correct, safe, predictable approach for a security system.
- Future work could explore an autonomous ("agentic") agent that manages signal weighting, retraining schedules, and threshold tuning adaptively. BUT this introduces real risks around predictability and control — an autonomous decision-maker changing a security model on its own initiative could weaken what it is meant to protect. Would need careful evaluation. In security, predictable and controlled generally beats clever and autonomous.

---

## 7. Combining with other authentication types
- Combine a one-time physiological check at login (e.g. fingerprint or face via WebAuthn/passkeys) with continuous behavioural monitoring during the session. Best of both: physiological for the front door, behavioural for the whole visit.
- Physiological signals such as EEG or ECG are extremely hard to fake and appear in the literature, but require specialist hardware and raise additional privacy/ethics considerations, placing them beyond a software-only PoC. Noted as a frontier direction.

---

## 8. Deployment and productionisation
- Move from local single-machine demo to a hosted deployment.
- Cross-platform key storage (not just macOS Keychain).
- Integration, security auditing, regulatory compliance (e.g. UK GDPR for behavioural data as special-category data), and staff training would be the main real-world costs of a production system.
