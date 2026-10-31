# Authentication

Brinkpy CLI requires authentication with the Brinkpy API to run analyses, design workflows, and simulations.

Authentication is provided through [Auth0](https://auth0.com), a widely used identity platform.

!!! info "Automatic authentication"
    You do not need to authenticate manually before using Brinkpy CLI. The first time you run `analyze`, `design`, or `simulate`, the CLI checks for a valid token. If none is found, it starts the sign-in flow before the command proceeds. Later commands reuse the stored token. Other commands, such as `profile` and `examples`, do not require sign-in.

    You can also sign in at any time using `brinkpy user auth`.

## Authenticate User

Start the sign-in flow to obtain an access token:

```bash
brinkpy user auth
```

The sign-in flow works as follows:

1. Brinkpy prints a sign-in link and a user code, and opens the link in your browser at `auth.brinkpy.app`.
2. Check that the code shown in the browser matches the code printed in the terminal.
3. **First time:** select **Sign up** to create your account. On later sign-ins, select **Log in**.
4. Authorize the application.
5. Return to the terminal. Sign-in completes automatically.

The sign-in link already includes the user code, so you do not need to type it.

## Check Authentication Status

Show the user ID of the account you are signed in with:

```bash
brinkpy user id
```

This prints `User is authenticated as:` followed by your user ID, or `User is not authenticated.` if no sign-in information is stored. The command only reads the stored sign-in information. It does not check whether the token has expired. Brinkpy handles expired tokens automatically the next time you run `analyze`, `design`, or `simulate`.

## Authentication Notes

- Brinkpy refreshes expired access tokens automatically. You are asked to sign in again only if the refresh fails.
- The CLI uses only public Auth0 values (domain, client ID, and audience) and does not store any client secret.
- Sign-in information is sent only to Auth0 (to sign in and refresh tokens) and to the Brinkpy API.
- Tokens are stored in a file named `auth_tokens.json` in your user configuration folder:
    - macOS: `~/Library/Application Support/Brinkpy/`
    - Linux: `~/.config/Brinkpy/`
    - Windows: `%LOCALAPPDATA%\Brinkpy\Brinkpy\`

    On macOS and Linux, the file can be read only by your user account. Deleting the file signs you out.

## Troubleshooting

Brinkpy checks whether your stored token is still valid, refreshes it when possible, and starts a new sign-in when required. If you still have problems:

1. Make sure you have an active internet connection.
2. Check that you can open `https://auth.brinkpy.app` in your browser.
3. If you see `Device code expired`, run the command again to start a new sign-in.
4. Sign in again with `brinkpy user auth`.
5. To force a fresh sign-in, delete the `auth_tokens.json` file (see [Authentication Notes](#authentication-notes)) and run `brinkpy user auth`.

For persistent issues, contact support at [brinkpy.app@gmail.com](mailto:brinkpy.app@gmail.com).
