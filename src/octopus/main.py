import argparse
import re

from pathlib import Path
from typing import Optional

from .builder import BuilderFutterIOS, BuilderFutterAndroid
from .git import GitManager
from .helper import FlutterMainFinder, FlutterMelosChecker


# Main entry point for the Octopus CI/CD tool.
def run_command() -> None:
    parser = argparse.ArgumentParser(
        description="iOS/Android CI/CD Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""""",
    )
    parser.add_argument("--run", action="store_true", help="Command to run")
    parser.add_argument(
        "--framework",
        type=str,
        help="Framework to use for the build",
        choices=["flutter"],
    )
    parser.add_argument(
        "--platform",
        type=str,
        help="Platform to build for (ios/android)",
        choices=["ios", "android"],
    )
    parser.add_argument("--flavor", type=str, help="Flavor of the build (optional)")
    parser.add_argument(
        "--provisioning-profile",
        type=str,
        help="Provisioning profile for iOS builds (optional)",
    )
    parser.add_argument("--git", type=str, help="Git repository URL (optional)")
    parser.add_argument("--branch", type=str, help="Git branch to checkout (optional)")

    args = parser.parse_args()

    if args.platform is not None:
        build(
            platform=args.platform,
            framework=args.framework if args.framework else None,
            flavor=args.flavor if args.flavor else None,
            provisioning_profile=(
                args.provisioning_profile if args.provisioning_profile else None
            ),
            git_url=args.git if args.git else None,
            branch=args.branch if args.branch else None,
        )


# Builds the App for the specified platform and flavor.
def build(
    platform: str,
    framework: Optional[str] = None,
    flavor: Optional[str] = None,
    provisioning_profile: Optional[str] = None,
    git_url: Optional[str] = None,
    branch: Optional[str] = None,
) -> None:
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
            print(f"❌ The specified {local_path} does not exist.")
            return

        # Flutter Melos Checker Processing
        checker = FlutterMelosChecker(local_path)
        if checker.has_melos_config():
            # Bootstrap 실행
            success, message = checker.run_melos_bootstrap(verbose=True)
            print(f"success: {success}, message: {message}")

        # Flutter Main Finder Processing
        finder = FlutterMainFinder(f"./{local_path}", recursive_search=True)
        finder.find_main_functions()
        entry_points = finder.get_flutter_entry_points()
        entry_path = (entry_points[0] if entry_points else {}).get("file", "")
        dir_app_path = Path(f"./{local_path}/{entry_path}").parent.parent
        if not dir_app_path.exists():
            print(f"❌ The specified {dir_app_path} does not exist.")
            return

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
            )
        output_file_path = builder.build()
        if not output_file_path:
            print("❌ Build failed.")
            return
        print(f"Output file: {output_file_path}")


if __name__ == "__main__":
    run_command()
