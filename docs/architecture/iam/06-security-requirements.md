# 06 - IAM Security Requirements and Verification

**Status:** Draft for review  
**Parent:** [IAM Architecture](README.md)

## 1. Purpose

Collect cross-cutting security requirements that apply to identity, authentication, account lifecycle, tokens, authorization, clients, and operations. These requirements complement the detailed flows and models in the other IAM documents.

## 2. Identity and account lifecycle

- **IAM-SEC-001:** The backend must verify Google ID tokens before accepting Google identity claims.
- **IAM-SEC-002:** The backend must validate token signature, issuer, audience, expiry, and nonce when applicable.
- **IAM-SEC-003:** Google identity association must use the verified issuer/provider and stable `sub`; email-only account matching is prohibited.
- **IAM-SEC-004:** An external identity must not be linked to more than one AMS account.
- **IAM-SEC-005:** Student registration must be controlled by backend eligibility and registration policy.
- **IAM-SEC-006:** Lecturer activation must operate only on an existing administrator-provisioned lecturer account.
- **IAM-SEC-007:** Lecturer self-registration and automatic lecturer account creation are prohibited.
- **IAM-SEC-008:** Identity linking, activation, account-state changes, and privileged role changes must be protected and auditable.

## 3. Authentication and token lifecycle

- **IAM-SEC-009:** AMS authentication must issue a short-lived access JWT and refresh JWT only after successful identity and account eligibility checks.
- **IAM-SEC-010:** Refresh-token rotation and blacklist/replay rejection must be enforced server-side.
- **IAM-SEC-011:** A refresh token must be rejected after its 14-day inactivity expiry or after it has been rotated/blacklisted.
- **IAM-SEC-012:** The client must securely persist both replacement tokens after successful refresh.
- **IAM-SEC-013:** Clients must not retry an unauthorized request indefinitely; retry at most once after successful refresh.
- **IAM-SEC-014:** Logout must clear local credentials and invoke backend refresh-token revocation where supported.
- **IAM-SEC-015:** The absence of an absolute session lifetime in the initial release must be documented as a known limitation and future hardening item.

## 4. Authorization

- **IAM-SEC-016:** Django must be the authoritative enforcement point for role and permission decisions.
- **IAM-SEC-017:** A valid token alone must not authorize access to a resource.
- **IAM-SEC-018:** Protected operations must enforce role/capability and object-level ownership/scope rules.
- **IAM-SEC-019:** Student, Lecturer, HOD, and Administrator are distinct roles; one account may hold multiple roles.
- **IAM-SEC-020:** Roles must not imply unapproved privilege inheritance. Delegated HOD administrative permissions must be explicit and appropriately scoped.
- **IAM-SEC-021:** Administrative provisioning and role-management endpoints must require dedicated permissions.
- **IAM-SEC-022:** Authorization must fail closed when the principal's account state, resource ownership, or scope cannot be verified.

## 5. Client and transport security

- **IAM-SEC-023:** Production API communication must use HTTPS.
- **IAM-SEC-024:** Flutter applications must not contain confidential backend or Google client secrets.
- **IAM-SEC-025:** AMS access and refresh tokens must be stored using platform-appropriate secure storage.
- **IAM-SEC-026:** Client logs must not contain passwords, tokens, activation credentials, authorization headers, or sensitive authentication payloads.
- **IAM-SEC-027:** Client-side route guards and hidden UI controls must not be relied upon for authorization.

## 6. Secrets, configuration, and audit

- **IAM-SEC-028:** Secrets and private keys must not be committed to source control.
- **IAM-SEC-029:** Exposed credentials and keys must be treated as compromised, rotated, and removed from active use; deleting a file from the latest commit alone is insufficient if history remains exposed.
- **IAM-SEC-030:** Development and production configuration must be separated; production must not implicitly load development dotenv values.
- **IAM-SEC-031:** Security events must be auditable without storing credentials, raw tokens, private keys, or sensitive request bodies.
- **IAM-SEC-032:** Authentication and registration errors must avoid unnecessary account enumeration.

## 7. Minimum verification matrix

| Area | Positive tests | Negative/security tests |
|---|---|---|
| Google OIDC | Valid token for approved client | Invalid signature, wrong issuer/audience, expired token, invalid nonce when used |
| Identity linking | First valid link to eligible account | Duplicate subject, email-only claim attempt, identity already linked elsewhere |
| Student flow | Existing student login; eligible registration completion | Ineligible registration; attempt to obtain privileged role; incomplete registration |
| Lecturer flow | Activation of provisioned lecturer account | Missing account; expired/reused invitation; claim another account; self-registration |
| Account state | Active account authenticates | Suspended/deactivated/ineligible account rejected |
| Token lifecycle | Issue, refresh, rotate, logout | Expiry, blacklist/reuse, concurrent refresh, post-logout refresh |
| Authorization | Allowed role and in-scope resource | Cross-role, cross-user, cross-department, changed object ID, missing permission |
| Delegation | HOD performs explicitly delegated in-scope operation | HOD attempts unrelated/global administrator action |
| Client security | Secure token storage and account switching | Token leakage in logs; stale token retained after rotation/logout |
| Operations | Correct production secrets and HTTPS | Committed secrets, development config in production, sensitive logging |

## 8. Release security checklist

- [ ] Google OIDC validation is tested against invalid and wrong-audience tokens.
- [ ] Student registration and lecturer activation enforce distinct provisioning policies.
- [ ] Identity-link uniqueness and conflict handling are tested.
- [ ] Refresh rotation, blacklist, reuse rejection, and inactivity expiry are tested.
- [ ] Logout and account deactivation behavior are tested.
- [ ] Student/Lecturer/HOD/Administrator permission boundaries are tested.
- [ ] Object-level and cross-department access denials are tested.
- [ ] HOD delegated permissions are explicit, scoped, and audited.
- [ ] No secrets or private keys remain in active tracked files or unremediated repository history.
- [ ] Production settings, HTTPS, allowed hosts, CORS/CSRF where applicable, and secret loading are reviewed.
- [ ] Neither Flutter application logs credentials, tokens, or sensitive authentication payloads.
- [ ] API documentation matches implemented request, response, and error contracts.

## 9. Related tracked security work

- [#42 - Rotate exposed credentials and secure lecturer provisioning](https://github.com/GeinoX/ams-backend/issues/42)
- [#44 - Architecture and security foundations](https://github.com/GeinoX/ams-backend/issues/44)
- [#50 - Security, audit, end-to-end verification, and release](https://github.com/GeinoX/ams-backend/issues/50)

## 10. Open security decisions

- Absolute maximum session lifetime and enforcement mechanism.
- Refresh-token reuse response (reject only the reused token versus revoke the entire related token family).
- Access-token invalidation behavior after logout, account suspension, or administrative revocation.
- Final activation-invitation lifetime, delivery, storage, and recovery policy.
- Final permission catalog, HOD delegation policy, and scope model.
- Signing-key rotation and operational key-management procedure.
