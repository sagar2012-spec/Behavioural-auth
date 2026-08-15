# Limitations

Running list of honest limitations for the dissertation. Naming these clearly is a strength, not a weakness. Grouped by theme. Polish into prose later.

---

## 1. Signal-specific limitations

### Login timing signal
- Assumes the user types their credentials manually.
- Broken by password managers, browser autofill, and copy-paste, which fill the field automatically and remove or distort the natural timing.
- In these cases the timing signal becomes unreliable.
- Because the framework uses multiple signals and a majority vote, one weakened signal does not by itself cause a wrong decision. This affects the strength of one signal, not the overall design.

### IP and geolocation signal
- These are simulated (dummy values assigned per volunteer), not real, in the proof of concept.
- Real IP/geolocation is broken by VPNs and secure tunnels: the system sees the VPN server's location, not the user's.
- A genuine user on a VPN may appear to log in from different countries on different days (looks suspicious but is normal).
- Different users sharing the same VPN may appear to come from the same location (weakens the signal's ability to tell people apart).
- Treated as a weak contextual clue, not a strong identifier. One vote of several.

### Unifying insight (worth stating once, prominently)
- Both the login-timing and IP/location limitations share one theme: a signal becomes unreliable when an intermediary tool sits between the real user and what is measured. A password manager sits between the user and their typing; a VPN sits between the user and their location. This is precisely why a multi-signal design with a majority vote is more robust than any single-signal system.

### Keystroke dynamics signal
- Tested on 10 of 51 CMU users (can extend to all 51 — quick).
- Fixed-text only (everyone types the same password). Free-text keystroke dynamics is harder and is future work.
- Validated on the CMU benchmark dataset, not on live volunteer typing. Live capture in the app is optional/future work; with few volunteers typing few times, live results would be weaker due to limited training data.
- Cold-start: needs enough samples before it authenticates reliably.
- Single-signal performance is moderate (avg 75.6% genuine acceptance, 95.2% impostor rejection across 10 users). This is expected and acceptable because signals combine in a vote; it is not a standalone authenticator.

---

## 2. Passwordless / login-method limitations
- Login-moment signals (login timing, keystroke at login) assume a typed login.
- They are unavailable when the user authenticates with a passkey, fingerprint, or single sign-on, because there is no typing to observe.
- However, post-login behavioural signals (session behaviour, navigation, etc.) continue to work regardless of login method.
- Framing: the system is complementary to strong login methods, not a replacement. A passkey secures the entry point; behavioural authentication secures the ongoing session. A passkey proves who unlocked the session, not who is using it afterwards.

---

## 3. Blockchain / integrity limitations
- A single Ganache node is NOT truly decentralised — it only simulates the mechanism on one local machine. True decentralisation across many independent nodes is not achieved in the PoC.
- Ganache auto-mines (instant blocks), which removes the real latency and consensus behaviour of a live network.
- Blockchain integrity protects the RECORD, not the AUTHORISATION of whoever wrote it. An attacker who fully compromises the host and obtains the system's blockchain signing credentials could submit valid hashes for tampered patterns, and the integrity check would pass. This is an inherent property of hash-anchoring, not a flaw specific to this design.
- Only the hash is protected on-chain; the raw local pattern data is not itself on the blockchain.

---

## 4. Data storage / privacy limitations
- Raw behavioural patterns are stored locally. If stored in plaintext, anyone with the database file could read them (addressed by encryption at rest — see below / future work).
- Encryption at rest protects the stored file when not in use; it does not protect data while the app is running (decrypted in memory) or against an attacker who has obtained the key.
- Key management is the hard part. For the PoC the key is held separately (environment variable / OS store), but production-grade key management (hardware security module, secrets manager) is future work.
- Behaviour cannot be used as the encryption key (unstable + circular dependency: need the data to authenticate, need authentication to decrypt the data).
- Passwordless secrets (passkey private keys, SSO tokens) cannot be used as the key either (inaccessible to the app and/or unstable across logins).

---

## 5. Evaluation / methodology limitations
- Small number of volunteers (mainly researcher + a few friends) for the live signals. Self-testing bias is a risk.
- IP and location are simulated, not real.
- Thresholds (e.g. 60% similarity, majority vote) are chosen for the PoC, not derived from large-scale data. They are design parameters, justified by the security-usability tradeoff observed, but not optimised.
- Only a subset of the designed signals is fully implemented (login timing, location, keystroke; others designed and noted as future work).
- Limited adversarial testing beyond the deliberate tamper test.
- Enrolment data quality matters: outlier sessions (e.g. a distracted login) can widen the learned pattern until it accepts almost anything. Observed directly when an early pattern had spread larger than its mean due to test outliers.

---

## 6. Scope limitations
- Desktop web app only. Touch gestures and device handling (accelerometer/gyroscope) are phone-only and not applicable; noted as future work / mobile extension.
- Runs locally, not deployed online. Single-machine demonstration.
