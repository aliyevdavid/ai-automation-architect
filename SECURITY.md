# Security Policy

## Supported version

Security fixes are currently considered for the latest commit on `main`. This repository does not currently represent a hosted production service.

## Reporting a vulnerability

Please report vulnerabilities privately through the repository's GitHub private vulnerability reporting feature when it is available. If that feature is unavailable, contact the repository owner privately through a contact method listed on the owner's GitHub profile.

Do not open a public issue containing:

- credentials, tokens, or private keys
- personal, customer, employer, or proprietary data
- exploit instructions or unredacted vulnerable payloads
- sensitive prompts, model responses, or project requirements

If a real credential has been exposed, revoke or rotate it immediately before reporting the incident. Do not include the credential value in the report.

A useful report includes the affected file or component, the impact, safe reproduction steps, and any suggested mitigation. Receipt and remediation timing depend on maintainer availability; this repository does not promise a formal service-level agreement.

## Scope

Reports may cover source code, dependency configuration, CI configuration, and unsafe handling of project requirements. Future AI integrations must treat prompts, responses, and submitted architecture context as potentially sensitive.

General feature requests, documentation corrections, and non-sensitive bugs may use the normal issue workflow.
