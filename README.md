# Octopus

Octopus is a powerful CI/CD tool designed for iOS and Android applications. It simplifies the deployment process for mobile apps built with Flutter, enabling seamless integration and delivery.

## Supported Platforms

- **Flutter** (iOS and Android)

## Features

- Automated build and deployment for Flutter apps.
- Support for multiple platforms (iOS and Android).
- Integration with Git repositories for version control.
- Easy configuration with provisioning profiles.

## Usage Example

To run the tool, use the following command:

```bash
poetry run poe run \
  --platform ios \
  --framework flutter \
  --provisioning-profile com.josephnk.mockup1-appstore \
  --git https://github.com/JosephNK/flutter_mockup1 \
  --branch main
```

### Command Breakdown

- `--platform ios`: Specifies the target platform (iOS or Android).
- `--framework flutter`: Indicates the framework used for the project.
- `--provisioning-profile com.josephnk.mockup1-appstore`: Sets the provisioning profile for iOS deployment.
- `--git https://github.com/JosephNK/flutter_mockup1`: Points to the Git repository containing the project source code.
- `--branch main`: Specifies the branch to be used for the build.