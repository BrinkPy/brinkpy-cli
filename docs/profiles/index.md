# Profile Management

Profiles are YAML configuration files that control run options for analysis, design, and simulation. The `default` profile is built-in and cannot be modified.

For detailed documentation of all available profile options, see the [Profile Options Reference](profile-reference.md).

## Creating a New Profile

Create a new profile with default settings:

Usage: `brinkpy profile new <name> [--description "Description"] [--force]`

Example:
```bash
brinkpy profile new custom --description "My custom profile"
```

## Editing Profiles

Edit an existing profile using your preferred editor:

Using nano:

Usage: `brinkpy profile nano <name>`

Using vim:

Usage: `brinkpy profile vim <name>`

Using vi (alias):

Usage: `brinkpy profile vi <name>`

Note: You can also manage profile YAML files directly in your IDE (for example, VS Code).

## Viewing Profiles

Display a profile's contents:

Formatted view:

Usage: `brinkpy profile show <name>`

Formatted view alias:

Usage: `brinkpy profile echo <name>`

Raw YAML view:

Usage: `brinkpy profile show <name> --raw`

Note: You can also manage profile YAML files directly in your IDE (for example, VS Code).

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

Example:
```bash
brinkpy profile copy default mycopy
```

Note: You can also manage profile YAML files directly in your IDE (for example, VS Code).

## Renaming Profiles

Rename a profile:

Usage: `brinkpy profile rename <old_name> <new_name> [--validate]`

Alias: `brinkpy profile mv <old_name> <new_name>`

Note: You can also manage profile YAML files directly in your IDE (for example, VS Code).

## Deleting Profiles

Delete a profile (requires confirmation):

Usage: `brinkpy profile delete <name>`

Aliases: `brinkpy profile del <name>`, `brinkpy profile rm <name>`

Note: You can also manage profile YAML files directly in your IDE (for example, VS Code).

Note: The `default` profile cannot be deleted.
