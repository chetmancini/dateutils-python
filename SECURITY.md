# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | Yes                |
| < 0.4   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in dateutils-python, please report it responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please send an email to **chetmancini@gmail.com** with:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes (if available)

You should receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity.

## Security Considerations

### Dependencies

This library has **zero external dependencies** beyond Python's standard library. This minimizes supply chain attack surface and reduces the need to track third-party security advisories.

### Input Validation

All public functions validate their inputs and raise appropriate exceptions for invalid data. However, as with any date/time library:

- Be cautious when parsing dates from untrusted user input
- Consider additional validation for your specific use case
- Timestamps outside reasonable ranges (e.g., year 1-9999) may behave unexpectedly

### Timezone Data

Timezone information comes from Python's `zoneinfo` module, which uses the system's IANA timezone database. Keep your system's timezone data updated for accurate conversions.
