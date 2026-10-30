# Profile Management

Profiles are YAML configuration files that control run options for analysis, design, and simulation. The `default` profile is built-in and cannot be modified.

Each profile you create is saved as `profiles/<name>.yaml` in your project folder. You can manage profiles with the commands on this page, or open and edit the YAML files directly in your IDE (for example, VS Code).

For detailed documentation of all available profile options, see the [Profile Options Reference](profile-reference.md).

## Typical Workflow

1. Create a profile with default settings:

    ```bash
    brinkpy profile new myprofile
    ```

2. Edit `profiles/myprofile.yaml` in your IDE, or with `brinkpy profile nano myprofile`.

3. Check the profile for errors:

    ```bash
    brinkpy profile validate myprofile
    ```

4. Use the profile in a run:

    ```bash
    brinkpy analyze myprofile
    ```

## Creating a New Profile

Create a new profile with default settings:

Usage: `brinkpy profile new <name> [--description "Description"] [--force]`

- `--description`, `-d`: A short description stored in the profile (default: `User-defined profile`)
- `--force`, `-f`: Overwrite the profile if one with the same name already exists

Example:
```bash
brinkpy profile new custom --description "My custom profile"
```

## Editing Profiles

Open a profile in a terminal text editor:

- `brinkpy profile nano <name>`: Edit with nano
- `brinkpy profile vim <name>`: Edit with vim (alias: `brinkpy profile vi <name>`)

These commands require nano or vim to be installed. They are usually available on macOS and Linux but not on Windows, where editing the YAML file in your IDE is the practical choice.

## Viewing Profiles

Display a profile's contents:

- `brinkpy profile show <name>`: Formatted view (alias: `brinkpy profile echo <name>`)
- `brinkpy profile show <name> --raw`: Raw YAML view (short form: `-r`)

## Listing All Profiles

List all available profiles:

```bash
brinkpy profile list
```

Alias:

```bash
brinkpy profile ls
```

## Validating Profiles

Validation checks the profile against the full option schema: verifies that all fields are recognized, required values are present, and values match the expected types and constraints.

Validate a profile's configuration:

Usage: `brinkpy profile validate <name>`

Alias: `brinkpy profile val <name>`

## Copying Profiles

Copy an existing profile:

Usage: `brinkpy profile copy <source> <destination> [--validate]`

Alias: `brinkpy profile cp <source> <destination>`

- `--validate`, `-v`: Validate the source profile before copying

Example:
```bash
brinkpy profile copy default mycopy
```

## Renaming Profiles

Rename a profile:

Usage: `brinkpy profile rename <old_name> <new_name> [--validate]`

Alias: `brinkpy profile mv <old_name> <new_name>`

- `--validate`, `-v`: Validate the profile before renaming

## Deleting Profiles

Delete a profile (requires confirmation):

Usage: `brinkpy profile delete <name>`

Aliases: `brinkpy profile del <name>`, `brinkpy profile rm <name>`

Note: The `default` profile cannot be deleted.
