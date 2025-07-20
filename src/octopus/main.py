import argparse
import re

from pathlib import Path
from typing import Dict, Optional

from .builder import BuilderFutterIOS, BuilderFutterAndroid
from .deploy import DeployAppStore, DeployGooglePlayStore, FastlaneRelease
from .git import GitManager
from .helper import FlutterMainFinder, FlutterMelosChecker


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
    deploy_parser.add_argument(
        "--build-file-path",
        type=str,
        required=True,
        help="Path to the build file (.ipa, .apk, or .aab)",
    )
    deploy_parser.add_argument(
        "--lane",
        type=str,
        required=True,
        help="Fastlane lane to use",
        choices=["dev_release", "auto_release"],
    )
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
        "--skip-binary-upload",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Skip binary upload (true/false, default: false)",
    )
    deploy_parser.add_argument(
        "--release-notes",
        type=str,
        help='Release notes as JSON string (e.g., \'{"ko":"Korean notes","en-US":"English notes"}\')',
    )

    args = parser.parse_args()

    if args.command == "build":
        result = build(
            platform=args.platform,
            framework=args.framework,
            git_url=args.git,
            flavor=args.flavor if args.flavor else None,
            provisioning_profile=(
                args.provisioning_profile if args.provisioning_profile else None
            ),
            branch=args.branch if args.branch else None,
        )
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

        print(f"Deploying with lane: {lane.value}")
        print(f"Build file path: {args.build_file_path}")
        print(f"iOS API Key ID: {args.ios_api_key_id}")
        print(f"iOS API Key Issuer ID: {args.ios_api_key_issuer_id}")
        print(f"Skip binary upload: {args.skip_binary_upload}")
        print(f"Release notes: {release_notes_dict}")

        result = deploy(
            build_file_path=args.build_file_path,
            lane=lane,
            ios_api_key_id=args.ios_api_key_id,
            ios_api_key_issuer_id=args.ios_api_key_issuer_id,
            ios_api_key_path=args.ios_api_key_path,
            skip_binary_upload=args.skip_binary_upload,
            release_notes=release_notes_dict,
        )
        if result:
            print("✅ Deployment completed successfully")
        else:
            print("❌ Deployment failed")


# Builds the App for the specified platform and flavor.
def build(
    platform: str,
    framework: str,
    git_url: str,
    flavor: Optional[str] = None,
    provisioning_profile: Optional[str] = None,
    branch: Optional[str] = None,
) -> Optional[str]:
    try:
        if not platform:
            raise ValueError("❌ Platform is required. Please specify --platform.")
        if not framework:
            raise ValueError("❌ Framework is required. Please specify --framework.")
        if not git_url:
            raise ValueError("❌ Git URL is required. Please specify --git.")

        if framework == "flutter":
            # Git Processing
            repo_name = GitManager.get_repo_name(git_url)
            git_manager = GitManager(
                repo_url=git_url,
                local_path=f"./repo/{repo_name}",
            )
            git_manager.checkout_branch(
                branch_name=branch if branch else "main",
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
            if platform == "ios":
                builder = BuilderFutterIOS(
                    build_path=dir_app_path,
                    flavor=flavor,
                    provisioning_profile=provisioning_profile,
                )
            elif platform == "android":
                builder = BuilderFutterAndroid(
                    build_path=dir_app_path,
                    flavor=flavor,
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


def deploy(
    build_file_path: str,
    lane: FastlaneRelease,
    ios_api_key_id: str,
    ios_api_key_issuer_id: str,
    ios_api_key_path: str,
    skip_binary_upload: bool = True,
    release_notes: Dict[str, str] = None,
) -> Optional[bool]:
    try:
        if not build_file_path:
            raise ValueError("❌ Output file path is required.")

        build_path = Path(build_file_path)
        if build_path.suffix not in [".ipa", ".apk", ".aab"]:
            raise ValueError(
                "❌ Unsupported file type. Only .ipa, .apk, or .aab files are allowed."
            )

        if build_path.suffix == ".ipa":
            print("📦 Deploying iOS app...")
            deploy = DeployAppStore(
                lane=lane,
                ipa_path=str(build_path),
                api_key_id=ios_api_key_id,
                api_key_issuer_id=ios_api_key_issuer_id,
                api_key_path=ios_api_key_path,
                skip_binary_upload=skip_binary_upload,
                release_notes=release_notes,
            )
            success = deploy.deploy()
        elif build_path.suffix == ".apk":
            print("📦 Deploying Android app...")
            raise ValueError(
                "❌ Unsupported Android APK deployment. Please use .aab for deployment.",
            )
        elif build_path.suffix == ".aab":
            print("📦 Deploying Android App Bundle...")
            deploy = DeployGooglePlayStore()
            success = deploy.deploy()

        return success
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False


if __name__ == "__main__":
    command()
