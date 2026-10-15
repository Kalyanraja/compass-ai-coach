# SYNTHETIC TRAINING STANDARD - for demo only, not a real enterprise policy

API Design Standard (synthetic), version 0.1

This document is a made-up standard used to demo how Compass checks an OpenAPI
spec against numbered requirements. It does not describe any real organization.

## Requirements

1. **STD-API-1** - Every operation declares a required header parameter `X-Correlation-Id` (in: header, required: true).
2. **STD-API-2** - Every POST and PUT operation documents a `400` response whose body uses an error schema with fields `code` and `message`.
3. **STD-API-3** - Operations require bearer authentication: the spec defines `components.securitySchemes.bearerAuth` (type: http, scheme: bearer) and applies it through `security`.
4. **STD-API-4** - Request bodies mark their required fields with a `required` list.
5. **STD-API-5** - No secrets or personal data are written to logs.
