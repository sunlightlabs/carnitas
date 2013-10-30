# Carnitas

Braised pork is delicious. So are API keys.

Carnitas provides email-based key registration for [Sunlight Foundation APIs](http://sunlightfoundation.com/api/).


## Configuration

| Environment Variable | Value |
| ---- | ---- |
| SERVICE_EMAIL | The email address that will receive key requests |
| POSTMARK_KEY | Key from Postmark |
| POSTMARK_SENDER | The email address that will send the key responses |
| SUNLIGHT_KEY | Sunlight Foundation API key |
| SUNLIGHT_SECRET | Sunlight Foundation secret key |
| SUNLIGHT_URL | URL for Sunlight key registration endpoint |
| SENTRY_DSN | Sentry DSN (optional) |
| REGISTRATION_ENABLED | If this variable is present, registration is enabled |
