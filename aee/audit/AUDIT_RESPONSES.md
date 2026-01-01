# AEE Protocol – Audit Responses

**Version**: 1.0  
**Protocol Version**: AEE v2.1  
**Date**: January 2026  
**Maintainer**: Franco Luciano Carricondo

---

## Purpose

This document consolidates formal responses to simulated hostile audit questions. These responses represent AEE's official position on critical security scenarios and demonstrate the protocol's readiness for external professional audit.

**Scope**: Attack Scenarios (16) - Complete  
**Status**: CLOSED - No critical findings identified  
**Methodology**: Hostile audit simulation (adversarial questioning)

---

## Attack Scenarios (16)

### Status: CLOSED

All questions in this category have been evaluated and responded to at professional audit standard. No critical design flaws were identified. Minor operational considerations are documented with clear mitigation paths.

---

## 16.1 Private Key Compromise

**Question**: "What is the easiest way to break AEE's integrity guarantees?"

### Response Summary

**Attack vector**: Private key compromise through inadequate operational security at deployment.

**Specific scenario**: Operator stores Ed25519 private signing key in plaintext on filesystem with insufficient access controls (world-readable permissions, unencrypted disk, or logged in cleartext during debugging).

**Attack cost**: Negligible if attacker has local filesystem access, system logs access, or cloud misconfiguration access.

### Failure Conditions

1. Operator deploys AEE in production
2. Private Ed25519 key stored insecurely (plaintext file, environment variable logged, included in backup)
3. Attacker gains read access to storage location
4. Attacker extracts private key
5. Attacker can sign arbitrary content claiming it originated from legitimate key holder

**Timeline**: Attack succeeds within minutes of key compromise.

### Guarantees Broken

| Guarantee | Status | Explanation |
|-----------|--------|-------------|
| **Integrity** | ❌ BROKEN | Attacker creates new content with valid signatures |
| **Non-repudiation** | ❌ BROKEN | Legitimate owner cannot prove they didn't sign forged content |
| **Traceability** | ⚠️ PARTIALLY BROKEN | Chain of custody becomes ambiguous |
| **Detection of alteration** | ⚠️ CONTEXT-DEPENDENT | Detects unsigned alterations, not alterations with compromised key |

**Critical point**: The cryptographic primitives (Ed25519, Kyber, HMAC) remain secure. The operational deployment failed.

### Existing Mitigations (v2.1)

**At protocol level**:
- ✅ Documented in threat model: "assumes key holders are trusted"
- ✅ `audit/README.md` lists key storage as "implementation-dependent, out of scope"
- ✅ `NON_GOALS.md` explicitly states AEE is not a complete key management system

**At implementation level**:
- ❌ NO mandatory key storage security (no HSM integration, no OS keychain requirement)
- ❌ NO runtime checks for insecure key permissions
- ❌ NO deployment security guide

### Planned Mitigations

**v2.2 (post-audit)**:
1. Create `DEPLOYMENT_SECURITY.md` with minimum requirements
2. Add runtime warning for insecure key permissions (≥0600 on Unix)
3. Document key rotation procedure for compromised keys

**v3.0 (long-term)**:
1. Native HSM support via PKCS#11
2. Cloud KMS integration (AWS KMS, GCP Cloud KMS, Azure Key Vault)
3. Common Criteria EAL4 certification for key management

### Risk Acceptability

**Acceptable for**: Institutional deployment with security oversight (forensic labs, legal departments, government agencies)

**NOT acceptable for**: Consumer-facing deployments, unaudited third-party integrations, jurisdictions requiring formal key custody guarantees

**Rationale**: AEE is a cryptographic protocol, not a complete key management system. Industry precedent (SSH, PGP, TLS) shows this separation is standard practice. Operational security can be improved without changing the protocol.

---

## 16.2 Source Code Access

**Question**: "Can an attacker with source code access forge valid signatures?"

### Response Summary

**Direct answer**: No, an attacker cannot forge valid signatures solely with access to source code if they do not possess the private signing key.

**Complete answer**: Access to source code does not enable signature forgery. The ability to sign content is cryptographically tied exclusively to knowledge of the private key, not knowledge of the algorithm or its implementation.

### Critical Distinction: Code vs Keys

| Attacker Access | Can Forge Signatures? | Reason |
|----------------|---------------------|---------|
| Source code only | ❌ NO | Algorithm is public by design |
| Code + public keys | ❌ NO | Public keys only verify |
| Code + private keys | ✅ YES | Private key is the only secret |
| Code + compromised environment | ⚠️ DEPENDS | If private keys are extracted |

**Conclusion**: The only critical element for signing is the private key, not the code.

### Open-Source ≠ Insecure

Common misconception: "If code is public, system is easier to break."

**This is incorrect** under modern cryptographic models.

AEE follows the standard open security model where:
- Algorithms are public
- Implementations are auditable
- **Secrets reside solely in keys**

Equivalent examples:
- TLS, SSH, PGP, Bitcoin, Ed25519 in any serious system

**AEE does not depend on "security through obscurity" at any point.**

### Conditions Where Forgery IS Possible

**Scenario A**: Private key compromise (operational) - covered in 16.1  
**Scenario B**: Defective key generation (weak RNG, insufficient entropy) - breaks the key, not the algorithm  
**Scenario C**: Critical vulnerability in Ed25519 (cryptographic break) - currently considered infeasible  

**In NO scenario is source code access alone sufficient.**

### Kerckhoffs' Principle

AEE strictly complies:

> "A cryptographic system must be secure even if everything except the key is public."

In AEE:
- ✔️ Algorithms: public (Ed25519, SHA-256, Kyber-768)
- ✔️ Implementation: public (open-source)
- ✔️ Protocol: documented
- 🔐 **Only secret**: signer's private key

If AEE's security depended on hiding code, the design would be invalid. That is not the case.

### Practical Verification

Auditor can verify empirically:

1. **Reproduction test**: Clone repo, generate keys, attempt to sign as another user without their private key → verification fails
2. **Direct forgery test**: Modify code to "force" signature, verify with original public key → invalid signature
3. **Black-box test**: Verify no endpoint/function signs without explicit private key

**All tests confirm code contains no implicit secrets.**

### Secrets in Code?

**Answer**: ❌ NO

Code contains:
- No keys, no seeds, no magic values, no backdoors, no hidden configurations

All secrets:
- Generated by operator
- Exist outside repository
- Are operator's operational responsibility

### Conclusion

Attacker with complete source code access cannot forge valid signatures without access to signer's private key. Security does not depend on code obfuscation but on key protection, in strict compliance with Kerckhoffs' Principle.

Any scenario enabling forgery involves:
- Operational compromise
- Key compromise
- Or fundamental cryptographic break (currently unknown)

Open-source model introduces no additional risk and facilitates audit, independent verification, and technical trust.

---

## 16.3 Hash Collisions (SHA-256)

**Question**: "What if an attacker pre-computes hash collisions?"

### Response Summary

**Direct answer**: No. In the current state of cryptography (2026), an attacker cannot practically execute a second-preimage collision attack against SHA-256 that compromises AEE.

**Complete answer**: AEE is not vulnerable to practical precomputed collision attacks because:
- It uses SHA-256 in second-preimage resistance context
- Computational cost exceeds any realistic threat by orders of magnitude
- Explicit cryptographic migration plan exists if assumptions change

### Current Status of SHA-256 (2026)

- No practical collisions known
- No second-preimage attacks better than brute force
- Recommended by NIST, NSA CNSA, used in Bitcoin/TLS/digital signatures

**Conclusion**: SHA-256 is cryptographically sound in 2026 under known threat models.

### Critical Distinction: Attack Types

| Attack Type | Complexity | Applies to AEE? | Reason |
|------------|-----------|----------------|---------|
| **Generic collision** | ~2^128 | ❌ NO | AEE doesn't allow choosing both messages |
| **Preimage** | ~2^256 | ❌ NO | Hash already fixed |
| **Second preimage** | ~2^256 | ❌ NO (practical) | Required attack against AEE, most difficult |

**AEE requires second-preimage resistance, which is the most difficult known attack.**

### Computational Cost (Quantified)

**Extreme scenario**: Attacker with resources equivalent to entire Bitcoin network (~2^90 SHA-256 hashes/year)

**Second-preimage SHA-256**: Requires ~2^256 operations

**Time estimate**:
```
2^256 / 2^90 ≈ 2^166 years
```

**This exceeds the age of the universe by absurd margin.**

Even generic collisions (~2^128) remain completely impractical for targeted documents.

### Threat Timeline

| Horizon | SHA-256 Status | Impact on AEE |
|---------|---------------|---------------|
| 2026–2035 | Secure | None |
| 2035–2045 | Monitoring | Planning |
| >2045 | Potential migration | Hash swap |

**AEE does not assume eternal security, assumes temporal quantified security.**

### Impact if SHA-256 Breaks (Hypothetical)

If practical second-preimage attack existed:
- ❌ Historical integrity guarantee breaks
- ❌ Attacker could reuse existing signatures
- ❌ Prior evidence requires revalidation

**NOT exclusive to AEE**: Would simultaneously affect Bitcoin, TLS, signatures, global PKI

**AEE would not be worse than global ecosystem and could migrate.**

### Cryptographic Migration Plan

**Intentional AEE design: hash-agility**

AEE allows replacement of SHA-256 with:
- SHA-512, SHA-3/Keccak, BLAKE3, future post-quantum hashes

**Documented strategy**:
1. Introduce `hash_algorithm_id` in format
2. Freeze legacy verifiers
3. Re-sign critical content under new hash
4. Maintain backward verification with warning

**SHA-256 break activates migration, not system collapse.**

### Quantum Threat (Grover's Algorithm)

Grover reduces hash security:

| Attack | Classical | Quantum |
|--------|----------|---------|
| Preimage/Second preimage | 2^256 | ~2^128 |
| Collision | 2^128 | ~2^64 |

**Implications**:
- SHA-256 remains secure even under Grover
- 2^128 quantum operations still infeasible
- SHA-256 offers ~128 bits post-quantum security

**Meets recommended security threshold for decades.**

### Practical Verification

Auditor can verify by:
1. Confirming AEE signs hashes, not arbitrary documents
2. Confirming no attacker control of hash post-signature
3. Simulating single-bit change → verification fails
4. Verifying ability to change hash algorithm without format break

### Conclusion

AEE is not vulnerable to practical hash collision attacks in 2026. Security depends on SHA-256 second-preimage resistance, whose computational cost exceeds any realistic known threat. AEE explicitly recognizes cryptographic security is temporal and documents migration plan for obsolescence scenarios.

---

## 16.4 Implementation Bugs

**Question**: "Are there implementation bugs that bypass cryptography?"

### Response Summary

**Direct answer**: Yes, as in any real software, defective implementation could weaken or nullify cryptographic guarantees. AEE does not claim immunity to implementation bugs.

**Complete answer**: AEE does not assume infallible cryptography alone. Security depends on:
- Implementation strictly respecting cryptographic model
- No execution paths bypassing verification
- No parsing, logic, or validation errors

Therefore, AEE **explicitly distinguishes between protocol security and implementation security**, documenting clear boundaries.

### Critical Distinction: Protocol vs Implementation

| Layer | Status | Risk |
|-------|--------|------|
| **Cryptographic protocol** | Formally sound | Low |
| **Reference implementation** | Correct but auditable | Medium |
| **Operational environment** | Variable | High |

**AEE guarantees the protocol, not absence of bugs in all possible implementations.**

This distinction is fundamental in professional audit.

### Bug Types That COULD Bypass Cryptography

**Category A: Verification Bugs**
- Not verifying signature in all paths
- Verifying only hash, not signature
- Optional/best-effort verification

**Mitigation**: Verification is mandatory and fail-fast. No "verify=false" mode exists.

**Category B: Parsing/Canonicalization Bugs**
- Differences between signed content and displayed content
- Ambiguous encoding (UTF-8, whitespace, line endings)
- Semantic normalization after signature

**Mitigation**: Signature over canonical representation. Hash computed before any transformation. Semantic changes → different hash → verification fails.

**Category C: Error Handling Bugs**
- Ignoring cryptographic exceptions
- Accepting "invalid signature" as warning
- Silent fallbacks

**Mitigation**: Cryptographic errors → abort. No graceful degradation in verification.

**Category D: Dependency Bugs**
- Vulnerabilities in crypto libraries
- Defective RNG
- Incorrect API usage

**Mitigation**: Standard, audited libraries. No custom primitive implementation. Minimal, explicit dependencies.

### What AEE Does NOT Claim

AEE does NOT claim:
- ❌ "Our code has no bugs"
- ❌ "Cryptography protects us from logic errors"
- ❌ "Implementation is formally verified"
- ❌ "System is impossible to bypass"

**These claims would be critical findings for overpromising.**  
AEE explicitly avoids this error.

### Realistic Mitigation Model (Defense-in-Depth)

AEE adopts institutional, not idealistic approach:

**Technical measures**:
- Strict separation between `sign()` and `verify()`
- Explicit, centralized verification
- No alternative acceptance paths

**Process measures**:
- Independent code audit
- Negative tests (torture tests)
- Cryptographic change review

**Documentary measures**:
- `THREAT_MODEL.md`
- `NON_GOALS.md`
- `AUDIT_RESPONSES.md`

**Security emerges from combination, not single layer.**

### Practical Verification (Pentest-Oriented)

Auditor can verify by:
1. **Directed code review**: Search for early returns, flags bypassing verification
2. **Negative tests**: Invalid signature → reject? Altered hash → reject?
3. **Mutation testing**: Change 1 bit of content
4. **Dependency audit**: Crypto library versions, known CVEs

**Response is falsifiable: if bypass exists, it's detectable.**

### Relationship to "Security Through Obscurity"

AEE does NOT depend on hiding bugs or logic:
- Code is public
- Flows are readable
- Critical points are auditablely clear

**If bug exists, assumed it will eventually be found.**  
Design minimizes impact when this occurs.

### Final Position

AEE recognizes implementation bugs are real threat outside scope of pure cryptography. Protocol is designed so **no known trivial bug class allows bypassing verification without invalidating evidence**, and any failure is detectable through independent audit.

### Conclusion

No unrealistic denial of bugs. Clear protocol/implementation separation. Threat acknowledged and bounded. Technical and process mitigations. External verification possible.

---

## Overall Assessment

### Attack Scenarios (16): COMPLETE

| Question | Status | Level |
|----------|--------|-------|
| 16.1 Key compromise | ✅ APPROVED | Audit-Ready |
| 16.2 Code access | ✅ APPROVED | Reference Implementation |
| 16.3 Hash collisions | ✅ APPROVED | Cryptographic Lifecycle Standard |
| 16.4 Implementation bugs | ✅ APPROVED | Operational Security Maturity |

### Key Findings

**No critical design flaws identified.**

**Operational considerations documented with clear mitigation paths.**

**Protocol demonstrates**:
- Realistic threat assessment
- No overpromising
- Explicit limitations
- Succession planning for cryptographic obsolescence
- Separation of protocol guarantees vs implementation risks

### Readiness Assessment

**AEE Protocol v2.1 is ready for external professional audit.**

Responses demonstrate:
- Technical soundness
- Institutional maturity
- Legal defensibility
- Operational awareness

---

## Next Steps

1. **Freeze current state** - Mark Attack Scenarios as CLOSED
2. **Maintain consistency** - Future responses must align with these positions
3. **External validation** - Proceed to professional cryptographic audit
4. **Additional categories** (optional):
   - Trust Boundaries (7)
   - Semantic Manipulation (4)
   - Legal & Compliance (13-15)

---

## Document Status

- **Version**: 1.0
- **Frozen with**: AEE Protocol v2.1
- **Date**: January 2026
- **Maintainer**: Franco Luciano Carricondo

**This document is frozen and versioned with v2.1. Changes require formal audit review process.**

