# AMS Identity and Access Management (IAM) Architecture

**Status:** Draft for review  
**Owner:** AMS backend architecture  
**Authoritative repository:** `GeinoX/ams-backend`  
**Scope:** Django backend, Student Flutter application, Lecturer Flutter application, and Google OpenID Connect integration.

## 1. Purpose

This directory documents the intended IAM architecture for the Attendance Management System (AMS). It is the architectural reference for identity, account lifecycle, authentication, session management, authorization, trust boundaries, and related security requirements.

The documents describe architecture and security contracts. They do not claim that every described behavior is already implemented. Implementation status must be verified against code and tests.

## 2. Architecture decisions

The following decisions are taken from the AMS IAM workstream and are the baseline for this draft:

1. Django is the authoritative AMS identity and access-management system. A separate identity server is not introduced for the initial release.
2. Google is an external OpenID Connect (OIDC) identity provider. Django verifies Google ID tokens server-side.
3. The verified Google `sub` is the stable external subject identifier. Email or client-supplied profile data alone must never be used to claim or link an AMS account.
4. Students can authenticate with Google. The backend decides whether the verified identity belongs to an existing eligible student account or must complete student registration.
5. Lecturer accounts are provisioned by an authorized administrator before activation. Lecturer self-registration and automatic lecturer account creation are prohibited.
6. A lecturer activates an existing provisioned AMS account by linking a verified Google identity.
7. Django owns account state, role assignment, permission evaluation, token issuance, and object-level authorization.
8. Authentication uses a short-lived access JWT and a refresh JWT. Refresh tokens are rotated and previously used refresh tokens are blacklisted/rejected.
9. The refresh-token inactivity window is 14 days from the latest successful rotation. A successful rotation issues a replacement refresh token with a new 14-day expiry.
10. The proposed configurable access-token default is 10 minutes.
11. An absolute maximum session lifetime is deferred from the initial release and recorded as a future hardening consideration.

See [04 - Session Lifecycle](04-session-lifecycle.md) and [Architecture decision references](#8-related-implementation-tracking).

## 3. Documentation map

| Document | Responsibility |
|---|---|
| [01 - IAM Domain Model](01-domain-model.md) | Domain concepts, relationships, account lifecycle concepts, and invariants. |
| [02 - Trust Boundaries](02-trust-boundaries.md) | Trust zones, trust relationships, security responsibilities, and boundary controls. |
| [03 - Authentication Flows](03-authentication-flows.md) | Student Google authentication/registration and lecturer activation sequences. |
| [04 - Session Lifecycle](04-session-lifecycle.md) | Access/refresh token issuance, rotation, expiry, logout, and revocation. |
| [05 - Authorization Model](05-authorization-model.md) | Roles, permissions, role assignments, organizational scope, and access-control rules. |
| [06 - Security Requirements](06-security-requirements.md) | Cross-cutting security invariants, verification expectations, and unresolved decisions. |

## 4. System scope and actors

- **Student:** uses the Student Flutter application and may complete student registration after Google authentication.
- **Lecturer:** uses the Lecturer Flutter application and must activate an administrator-provisioned account.
- **Administrator:** provisions lecturer accounts and performs explicitly authorized administrative operations.
- **Head of Department (HOD):** reviews and decides departmental workflows, including student absence/excuse requests, and may receive explicitly delegated administrative permissions.
- **Google:** external OIDC identity provider.
- **Django backend:** authoritative IAM policy enforcement point and issuer of AMS API tokens.

Administrator and HOD are distinct roles. An account may hold multiple roles. Roles do not imply automatic inheritance of all permissions from another role. A HOD may receive selected administrative permissions explicitly, subject to scope and policy.

## 5. Architectural principles

- **Backend authority:** client UI state is never an authorization control.
- **Verified identity:** only server-verified OIDC claims can establish a Google external identity.
- **Explicit account association:** external identities are linked to existing AMS accounts only through an authorized, verified flow.
- **Least privilege:** grant only the permissions required for a role and its assigned scope.
- **Separation of authentication and authorization:** a valid token proves an authenticated principal; it does not grant unrestricted access.
- **Deny by default:** protected operations require an explicit authorization policy.
- **Auditable security events:** record security-relevant outcomes without recording passwords, tokens, private keys, or sensitive request bodies.
- **Client confidentiality:** mobile clients are public/untrusted clients; no embedded client secret is trusted.

## 6. Status and interpretation

This directory is a **Draft for review**. Statements explicitly labelled *decision* reflect the current tracked AMS architecture. Statements labelled *proposed control*, *design detail to confirm*, or *open question* are recommendations or details requiring review. A draft must not be interpreted as evidence that a control is implemented.

When implementation differs from an approved architecture decision, update the implementation or raise and approve an architecture change; do not silently redefine the architecture through code.

## 7. Change management

Changes to identity keys, account-linking rules, role semantics, token policy, trust boundaries, or authorization rules require review because they can affect all three AMS repositories. Keep the authoritative architecture here and link to it from the student and lecturer application repositories rather than maintaining independent copies.

## 8. Related implementation tracking

- [#43 - IAM Program](https://github.com/GeinoX/ams-backend/issues/43)
- [#44 - Architecture and security foundations](https://github.com/GeinoX/ams-backend/issues/44)
- [#45 - Identity and account lifecycle](https://github.com/GeinoX/ams-backend/issues/45)
- [#46 - Authentication and token lifecycle](https://github.com/GeinoX/ams-backend/issues/46)
- [#47 - Authorization, roles, and permissions](https://github.com/GeinoX/ams-backend/issues/47)
- [#48 - Student application integration](https://github.com/GeinoX/ams_student_app/issues/48)
- [#49 - Lecturer application integration](https://github.com/GeinoX/ams_teacher_app/issues/49)
- [#50 - Security, audit, end-to-end verification, and release](https://github.com/GeinoX/ams-backend/issues/50)
- [#29 - Backend Google OIDC authentication and JWT session lifecycle](https://github.com/GeinoX/ams-backend/issues/29)

**Superseded decision:** [#28 - Sliding JWT tokens](https://github.com/GeinoX/ams-backend/issues/28) is explicitly superseded. The current design is an access/refresh pair with refresh rotation and blacklist/revocation, not sliding JWT tokens.
