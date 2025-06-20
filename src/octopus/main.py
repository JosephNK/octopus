import argparse
from typing import Optional

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

    args = parser.parse_args()

    if args.app_path is not None and args.platform is not None:
        build(
            apppath=args.app_path,
            platform=args.platform,
            flavor=args.flavor if args.flavor else None,
            provisioning_profile=(
                args.provisioning_profile if args.provisioning_profile else None
            ),
        )


# Builds the App for the specified platform and flavor.
def build(
    apppath: str,
    platform: str,
    flavor: Optional[str] = None,
    provisioning_profile: Optional[str] = None,
) -> None:
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
