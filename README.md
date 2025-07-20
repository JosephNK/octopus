# 🐙 Octopus

<div align="center">

**A powerful CI/CD tool for mobile applications**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flutter](https://img.shields.io/badge/flutter-supported-blue.svg)](https://flutter.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/JosephNK/octopus)

</div>

## 📖 Overview

Octopus is a sophisticated CI/CD automation tool specifically designed for iOS and Android mobile applications. It streamlines the entire deployment pipeline for Flutter applications, providing seamless integration with version control systems and automated build processes.

## ✨ Key Features

- 🚀 **Automated Build & Deployment** - One-command build and deployment for Flutter apps
- 🎯 **Multi-Platform Support** - Native support for iOS and Android platforms
- 🔄 **Git Integration** - Seamless integration with Git repositories and branch management
- 🔧 **Easy Configuration** - Simple setup with provisioning profiles and certificates
- ⚡ **Fast Builds** - Optimized build processes for quick iterations
- 📱 **Flutter Ready** - Purpose-built for Flutter mobile applications

## 🛠 Supported Platforms

| Platform | Framework | Status |
|----------|-----------|--------|
| 📱 iOS | Flutter | ✅ Supported |
| 🤖 Android | Flutter | ✅ Supported |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Poetry package manager
- Flutter SDK (for Flutter projects)
- Xcode (for iOS builds)
- Android SDK (for Android builds)

### Installation

```bash
# Clone the repository
git clone https://github.com/JosephNK/octopus.git
cd octopus

# Install dependencies
poetry install
```

### Command Options

| Option | Description | Required | Example |
|--------|-------------|----------|---------|
| `--platform` | Target platform (ios/android) | ✅ | `ios`, `android` |
| `--framework` | Development framework | ✅ | `flutter` |
| `--provisioning-profile` | iOS provisioning profile | ❌ | `com.example.app-appstore` |
| `--git` | Git repository URL | ✅ | `https://github.com/user/repo` |
| `--branch` | Git branch to build | ❌ | `main`, `develop`, `release/1.0` |

### Examples

#### iOS Build
```bash
poetry run poe build \
  --platform ios \
  --framework flutter \
  --provisioning-profile com.josephnk.mockup1-appstore \
  --git https://github.com/JosephNK/flutter_mockup1 \
  --branch main
```

#### Android Build
```bash
poetry run poe build \
  --platform android \
  --framework flutter \
  --git https://github.com/JosephNK/flutter_mockup1 \
  --branch main
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**JosephNK**
- GitHub: [@JosephNK](https://github.com/JosephNK)

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- Fastlane for mobile deployment automation
- Poetry for Python dependency management

---

<div align="center">

Made with ❤️ by [JosephNK](https://github.com/JosephNK)

</div>