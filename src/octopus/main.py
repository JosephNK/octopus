import argparse
from pathlib import Path
import re
from typing import Optional

from .git import GitManager
from .builder import BuilderFutterIOS, BuilderFutterAndroid


# Main entry point for the Octopus CI/CD tool.
def run_command() -> None:
    parser = argparse.ArgumentParser(
        description="iOS/Android CI/CD Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""""",
    )
    parser.add_argument("--run", action="store_true", help="Command to run")
    parser.add_argument("--app-path", type=str, help="Path to the app directory")
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

    if args.app_path is not None and args.platform is not None:
        build(
            apppath=args.app_path,
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
    apppath: str,
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
            fresh_clone=False,
        )
        git_status = git_manager.get_status()
        local_path = Path(git_status["local_path"])
        print(f"Local Path: {local_path}")
        return
        if platform == "ios":
            builder = BuilderFutterIOS(
                build_path=apppath,
                flavor=flavor,
                provisioning_profile=provisioning_profile,
            )
        elif platform == "android":
            builder = BuilderFutterAndroid(
                build_path=apppath,
                flavor=flavor,
            )
        builder.build()


if __name__ == "__main__":
    run_command()
