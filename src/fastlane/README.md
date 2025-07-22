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

### ios print_build_info

```sh
[bundle exec] fastlane ios print_build_info
```

Print build information from IPA

### ios internal_release

```sh
[bundle exec] fastlane ios internal_release
```

Internal release

### ios production_release

```sh
[bundle exec] fastlane ios production_release
```

Production release

----


## Android

### android custom_lane

```sh
[bundle exec] fastlane android custom_lane
```

Description of what the lane does

### android validate_json_key

```sh
[bundle exec] fastlane android validate_json_key
```

Validate Play Store JSON key

### android build_debug

```sh
[bundle exec] fastlane android build_debug
```

Build APK for development

### android build_release

```sh
[bundle exec] fastlane android build_release
```

Build APK for release

### android build_aab

```sh
[bundle exec] fastlane android build_aab
```

Build AAB for Play Store

### android internal_release

```sh
[bundle exec] fastlane android internal_release
```

Internal release

### android production_release

```sh
[bundle exec] fastlane android production_release
```

Production release

----

This README.md is auto-generated and will be re-generated every time [_fastlane_](https://fastlane.tools) is run.

More information about _fastlane_ can be found on [fastlane.tools](https://fastlane.tools).

The documentation of _fastlane_ can be found on [docs.fastlane.tools](https://docs.fastlane.tools).
