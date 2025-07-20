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


## Android

### android custom_lane

```sh
[bundle exec] fastlane android custom_lane
```

Description of what the lane does

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

### android internal

```sh
[bundle exec] fastlane android internal
```

Deploy to Google Play Internal Testing

### android alpha

```sh
[bundle exec] fastlane android alpha
```

Deploy to Google Play Alpha Testing

### android beta

```sh
[bundle exec] fastlane android beta
```

Deploy to Google Play Beta Testing

### android release

```sh
[bundle exec] fastlane android release
```

Deploy to Google Play Store Production

### android dev_release

```sh
[bundle exec] fastlane android dev_release
```

Quick upload for development

### android auto_release

```sh
[bundle exec] fastlane android auto_release
```

Fully automated release to production

----

This README.md is auto-generated and will be re-generated every time [_fastlane_](https://fastlane.tools) is run.

More information about _fastlane_ can be found on [fastlane.tools](https://fastlane.tools).

The documentation of _fastlane_ can be found on [docs.fastlane.tools](https://docs.fastlane.tools).
