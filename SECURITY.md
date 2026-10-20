# Security and privacy

## Supported version

Security fixes are applied to the latest version on the default branch.

## Reporting an issue

Please do not publish credentials, private content, or exploit details in a
public issue. Use GitHub's **Security** tab and **Report a vulnerability** when
that option is available. If it is unavailable, open a public issue containing
only a short request for a private reporting channel.

Include the affected file or workflow, expected behavior, observed behavior,
and a minimal reproduction that contains no real secrets or personal data.

## Data handling

The included validator reads local text and configuration files and does not
transmit their contents. Installing the optional Python dependency may contact
the configured package index, but the validator itself makes no network calls.

The agent skill runs inside the user's chosen AI host. That host's privacy,
retention, and network policies still apply to any prompt or example supplied
to the model.
