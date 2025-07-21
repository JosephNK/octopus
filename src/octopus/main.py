import argparse

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .builder import BuilderFutterIOS, BuilderFutterAndroid
from .deploy import DeployAppStore, DeployGooglePlayStore, FastlaneRelease
from .git import GitManager
from .helper import FlutterMainFinder, FlutterMelosChecker


@dataclass
class BuildConfig:
    """Build configuration parameters for the application build process."""

    platform: str
    framework: str
    git_url: str
    flavor: Optional[str] = None
    provisioning_profile: Optional[str] = None
    branch: Optional[str] = None


@dataclass
class DeployConfig:
    """Deployment configuration parameters for the application deployment process."""

    # Build configuration (embedded from BuildConfig)
    platform: str
    framework: str
    git_url: str
    flavor: Optional[str] = None
    provisioning_profile: Optional[str] = None
    branch: Optional[str] = None

    # Deployment specific
    build_file_path: Optional[str] = None
    lane: Optional[FastlaneRelease] = None

    # iOS specific parameters
    ios_api_key_id: Optional[str] = None
    ios_api_key_issuer_id: Optional[str] = None
    ios_api_key_path: Optional[str] = None
    ios_skip_binary_upload: bool = (
        False  # iOS specific: skip binary upload to App Store Connect
    )
    ios_groups: Optional[str] = None  # iOS specific: groups to deploy to

    # Android specific parameters
    android_json_key_path: Optional[str] = None
    android_package_name: Optional[str] = None
    android_skip_upload_apk: bool = False  # Android specific: skip APK upload
    android_skip_upload_aab: bool = False  # Android specific: skip AAB upload
    android_validate_only: bool = (
        False  # Android specific: only validate, don't publish
    )
    # Common parameters
    release_notes: Optional[Dict[str, str]] = None

    def get_build_config(self) -> BuildConfig:
        """Extract BuildConfig from this DeployConfig."""
        return BuildConfig(
            platform=self.platform,
            framework=self.framework,
            git_url=self.git_url,
            flavor=self.flavor,
            provisioning_profile=self.provisioning_profile,
            branch=self.branch,
        )


# Main entry point for the Octopus CI/CD tool.
def command() -> None:
    parser = argparse.ArgumentParser(
        description="iOS/Android CI/CD Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""""",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the application")
    build_parser.add_argument(
        "--framework",
        type=str,
        required=True,
        help="Framework to use for the build",
        choices=["flutter"],
    )
    build_parser.add_argument(
        "--platform",
        type=str,
        required=True,
        help="Platform to build for (ios/android)",
        choices=["ios", "android"],
    )
    build_parser.add_argument(
        "--git",
        type=str,
        required=True,
        help="Git repository URL",
    )
    build_parser.add_argument(
        "--flavor",
        type=str,
        help="Flavor of the build (optional)",
    )
    build_parser.add_argument(
        "--provisioning-profile",
        type=str,
        help="Provisioning profile for iOS builds (optional)",
    )
    build_parser.add_argument(
        "--branch",
        type=str,
        help="Git branch to checkout (optional, default: main)",
    )

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the application")

    # Build configuration parameters
    deploy_parser.add_argument(
        "--framework",
        type=str,
        required=True,
        help="Framework to use for the build",
        choices=["flutter"],
    )
    deploy_parser.add_argument(
        "--platform",
        type=str,
        required=True,
        help="Platform to build for (ios/android)",
        choices=["ios", "android"],
    )
    deploy_parser.add_argument(
        "--git",
        type=str,
        required=True,
        help="Git repository URL",
    )
    deploy_parser.add_argument(
        "--flavor",
        type=str,
        help="Flavor of the build (optional)",
    )
    deploy_parser.add_argument(
        "--provisioning-profile",
        type=str,
        help="Provisioning profile for iOS builds (optional)",
    )
    deploy_parser.add_argument(
        "--branch",
        type=str,
        help="Git branch to checkout (optional, default: main)",
    )

    # Common parameters for both iOS and Android
    deploy_parser.add_argument(
        "--build-file-path",
        type=str,
        help="Path to the build file (.ipa, .apk, or .aab). If not provided, will build from source.",
    )
    deploy_parser.add_argument(
        "--lane",
        type=str,
        required=True,
        help="Fastlane lane to use",
        choices=["dev_release", "auto_release"],
    )
    deploy_parser.add_argument(
        "--release-notes",
        type=str,
        help='Release notes as JSON string (e.g., \'{"ko":"Korean notes","en-US":"English notes"}\')',
    )

    # iOS specific parameters
    deploy_parser.add_argument(
        "--ios-api-key-id",
        type=str,
        help="iOS App Store Connect API Key ID (required for iOS)",
    )
    deploy_parser.add_argument(
        "--ios-api-key-issuer-id",
        type=str,
        help="iOS App Store Connect API Key Issuer ID (required for iOS)",
    )
    deploy_parser.add_argument(
        "--ios-api-key-path",
        type=str,
        help="iOS App Store Connect API Key file path (required for iOS)",
    )
    deploy_parser.add_argument(
        "--ios-skip-binary-upload",
        type=lambda x: x.lower() == "true",
        default=False,
        help="iOS Skip binary upload (true/false, default: false)",
    )
    deploy_parser.add_argument(
        "--ios-groups",
        type=str,
        help="iOS groups to deploy to (optional)",
    )

    # Android specific parameters
    deploy_parser.add_argument(
        "--android-json-key-path",
        type=str,
        help="Android JSON key file path (required for Android)",
    )
    deploy_parser.add_argument(
        "--android-package-name",
        type=str,
        help="Android package name (required for Android)",
    )
    deploy_parser.add_argument(
        "--android-skip-upload-apk",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Android APK Skip binary upload (true/false, default: false)",
    )
    deploy_parser.add_argument(
        "--android-skip-upload-aab",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Android AAB Skip binary upload (true/false, default: false)",
    )
    deploy_parser.add_argument(
        "--android-validate-only",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Android Validate only (true/false, default: false)",
    )

    args = parser.parse_args()

    if args.command == "build":
        config = BuildConfig(
            platform=args.platform,
            framework=args.framework,
            git_url=args.git,
            flavor=args.flavor if args.flavor else None,
            provisioning_profile=(
                args.provisioning_profile if args.provisioning_profile else None
            ),
            branch=args.branch if args.branch else None,
        )
        result = build(config)
        if result:
            print(f"✅ Build completed successfully: {result}")
        else:
            print("❌ Build failed")

    elif args.command == "deploy":
        # Parse release notes if provided
        release_notes_dict = None
        if args.release_notes:
            try:
                import json

                release_notes_dict = json.loads(args.release_notes)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for release notes")
                return

        lane_mapping = {
            "dev_release": FastlaneRelease.DEV_RELEASE,
            "auto_release": FastlaneRelease.AUTO_RELEASE,
        }
        lane = lane_mapping[args.lane]

        config = DeployConfig(
            # Build configuration
            platform=args.platform,
            framework=args.framework,
            git_url=args.git,
            flavor=args.flavor if args.flavor else None,
            provisioning_profile=(
                args.provisioning_profile if args.provisioning_profile else None
            ),
            branch=args.branch if args.branch else None,
            # Deploy configuration
            build_file_path=args.build_file_path,
            lane=lane,
            release_notes=release_notes_dict,
            ios_api_key_id=args.ios_api_key_id,
            ios_api_key_issuer_id=args.ios_api_key_issuer_id,
            ios_api_key_path=args.ios_api_key_path,
            ios_skip_binary_upload=args.ios_skip_binary_upload,
            ios_groups=args.ios_groups,
            android_json_key_path=args.android_json_key_path,
            android_package_name=args.android_package_name,
            android_skip_upload_apk=args.android_skip_upload_apk,
            android_skip_upload_aab=args.android_skip_upload_aab,
            android_validate_only=args.android_validate_only,
        )
        result = deployment(config)
        if result:
            print("✅ Deployment completed successfully")
        else:
            print("❌ Deployment failed")


# Builds the App for the specified platform and flavor.
def build(config: BuildConfig) -> Optional[str]:
    try:
        if not config.platform:
            raise ValueError("❌ Platform is required. Please specify --platform.")
        if not config.framework:
            raise ValueError("❌ Framework is required. Please specify --framework.")
        if not config.git_url:
            raise ValueError("❌ Git URL is required. Please specify --git.")

        if config.framework == "flutter":
            # Git Processing
            repo_name = GitManager.get_repo_name(config.git_url)
            git_manager = GitManager(
                repo_url=config.git_url,
                local_path=f"./repo/{repo_name}",
            )
            git_manager.checkout_branch(
                branch_name=config.branch if config.branch else "main",
                strategy="preserve",
            )
            git_status = git_manager.get_status()
            local_path = Path(git_status["local_path"])
            if not local_path.exists():
                raise ValueError(f"❌ The specified {local_path} does not exist.")

            # Flutter Melos Checker Processing
            checker = FlutterMelosChecker(local_path)
            if checker.has_melos_config():
                # Bootstrap 실행
                success, message = checker.run_melos_bootstrap(verbose=True)
                if not success:
                    raise ValueError(f"❌ Melos bootstrap failed: {message}")

            # Flutter Main Finder Processing
            finder = FlutterMainFinder(f"./{local_path}", recursive_search=True)
            finder.find_main_functions()
            entry_points = finder.get_flutter_entry_points()
            entry_path = (entry_points[0] if entry_points else {}).get("file", "")
            dir_app_path = Path(f"./{local_path}/{entry_path}").parent.parent
            if not dir_app_path.exists():
                raise ValueError(f"❌ The specified {dir_app_path} does not exist.")

            # Build Processing
            if config.platform == "ios":
                builder = BuilderFutterIOS(
                    build_path=dir_app_path,
                    flavor=config.flavor,
                    provisioning_profile=config.provisioning_profile,
                )
            elif config.platform == "android":
                builder = BuilderFutterAndroid(
                    build_path=dir_app_path,
                    flavor=config.flavor,
                    use_appbundle=True,
                )
            output_file_path = builder.build()
            if not output_file_path:
                raise ValueError(f"❌ Build failed.")

            print(f"Output file: {output_file_path}")

            return str(output_file_path)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None


def deployment(config: DeployConfig) -> Optional[bool]:
    try:
        # First, perform the build if build_file_path is not provided or doesn't exist
        build_file_path = config.build_file_path
        build_path = Path(build_file_path) if build_file_path else None

        if not build_path or not build_path.exists():
            print("🔨 Build file not found or not provided. Starting build process...")

            # Extract build config and perform build
            build_config = config.get_build_config()
            build_result = build(build_config)

            if not build_result:
                raise ValueError("❌ Build failed during deployment process.")

            build_file_path = build_result
            build_path = Path(build_file_path)
            print(f"✅ Build completed: {build_file_path}")

        if build_path.suffix not in [".ipa", ".apk", ".aab"]:
            raise ValueError(
                "❌ Unsupported file type. Only .ipa, .apk, or .aab files are allowed."
            )

        if build_path.suffix == ".ipa":
            print("📦 Deploying iOS app...")
            deploy = DeployAppStore(
                lane=config.lane,
                file_path=str(build_path),
                api_key_id=config.ios_api_key_id,
                api_key_issuer_id=config.ios_api_key_issuer_id,
                api_key_path=config.ios_api_key_path,
                skip_binary_upload=config.ios_skip_binary_upload,
                groups=config.ios_groups,
                release_notes=config.release_notes,
            )
        elif build_path.suffix == ".apk":
            print("📦 Deploying Android app...")
            raise ValueError(
                "❌ Unsupported Android APK deployment. Please use .aab for deployment.",
            )
        elif build_path.suffix == ".aab":
            print("📦 Deploying Android App Bundle...")
            deploy = DeployGooglePlayStore(
                lane=config.lane,
                file_path=str(build_path),
                json_key_path=config.android_json_key_path,
                package_name=config.android_package_name,
                skip_upload_apk=config.android_skip_upload_apk,
                skip_upload_aab=config.android_skip_upload_aab,
                validate_only=config.android_validate_only,
                release_notes=config.release_notes,
            )

        return deploy.deploy()
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False


if __name__ == "__main__":
    command()
