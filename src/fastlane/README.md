fastlane documentation
----

# Installation

Make sure you have the latest version of the Xcode command line tools installed:

```sh
xcode-select --install
```

For _fastlane_ installation instructions, see [Installing _fastlane_](https://docs.fastlane.tools/#installing-fastlane)

# Available Actions

## iOS

### ios custom_lane

```sh
[bundle exec] fastlane ios custom_lane
```

Description of what the lane does

### ios export

```sh
[bundle exec] fastlane ios export
```

Export IPA with provisioning

### ios beta

```sh
[bundle exec] fastlane ios beta
```

Deploy to TestFlight for beta testing

### ios release

```sh
[bundle exec] fastlane ios release
```

Deploy to App Store with specified configuration

### ios dev_release

```sh
[bundle exec] fastlane ios dev_release
```

Quick upload for development

### ios auto_release

```sh
[bundle exec] fastlane ios auto_release
```

Fully automated release with review submission

----

This README.md is auto-generated and will be re-generated every time [_fastlane_](https://fastlane.tools) is run.

More information about _fastlane_ can be found on [fastlane.tools](https://fastlane.tools).

The documentation of _fastlane_ can be found on [docs.fastlane.tools](https://docs.fastlane.tools).
