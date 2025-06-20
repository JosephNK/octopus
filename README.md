# Octopus

This project is iOS/Android CI/CD Tool.

## Support Platform

- Flutter iOS/Android

## Example

Command 

```bash
poetry run poe run \
  --platform ios \
  --framework flutter \
  --provisioning-profile com.josephnk.mockup1-appstore \
  --git https://github.com/JosephNK/flutter_mockup1 \
  --branch main
```