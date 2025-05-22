# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Best Practices

When using dateutils-python, please follow these security best practices:

1. **Always use the latest version** of the package
2. **Validate all input** before passing it to dateutils functions
3. **Handle timezone information carefully** to prevent timezone-related vulnerabilities
4. **Be cautious with date parsing** from untrusted sources
5. **Use appropriate error handling** for all date operations

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.0 -> 0.1.1). We recommend:

- Regularly updating to the latest version
- Subscribing to GitHub security alerts for this repository
- Following our release notes for security-related changes

## Dependencies

`dateutils-python` has minimal external dependencies to reduce the attack surface. We:

- Regularly audit our dependencies
- Use dependency pinning for reproducible builds
- Monitor for security vulnerabilities in dependencies

## License

This security policy is licensed under the MIT License - see the LICENSE file for details.
