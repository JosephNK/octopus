import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class FlutterMelosChecker:
    """Class to check for melos.yaml file existence in Flutter projects"""

    def __init__(self, project_path: str = "."):
        """
        Initialize FlutterMelosChecker

        Args:
            project_path (str): Project path (default: current directory)
        """
        self.project_path = Path(project_path).resolve()
        self.melos_files = ["melos.yaml", "melos.yml"]

    def has_melos_config(self) -> bool:
        """
        Check if melos.yaml or melos.yml file exists

        Returns:
            bool: True if melos config file exists, False otherwise
        """
        for filename in self.melos_files:
            if (self.project_path / filename).exists():
                return True
        return False

    def run_melos_bootstrap(self, verbose: bool = False) -> Tuple[bool, str]:
        """
        Execute melos bootstrap command

        Args:
            verbose (bool): Show detailed output during execution

        Returns:
            Tuple[bool, str]: (success, output_message)
        """
        # Check if melos config exists first
        if not self.has_melos_config():
            return (
                False,
                "❌ No melos config file found. melos.yaml or melos.yml is required.",
            )

        try:
            print(f"🚀 Running melos bootstrap in {self.project_path}...")

            # Execute melos bootstrap command
            result = subprocess.run(
                ["melos", "bootstrap"],
                cwd=self.project_path,
                capture_output=not verbose,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                success_msg = "✅ Melos bootstrap completed successfully!"
                if verbose and result.stdout:
                    success_msg += f"\n📄 Output:\n{result.stdout}"
                print(success_msg)
                return True, success_msg
            else:
                error_msg = (
                    f"❌ Melos bootstrap failed with exit code {result.returncode}"
                )
                if result.stderr:
                    error_msg += f"\n🔥 Error:\n{result.stderr}"
                print(error_msg)
                return False, error_msg

        except subprocess.TimeoutExpired:
            timeout_msg = "⏰ Melos bootstrap timed out after 5 minutes"
            print(timeout_msg)
            return False, timeout_msg

        except FileNotFoundError:
            not_found_msg = "❌ Melos command not found. Please install melos first:\n💡 dart pub global activate melos"
            print(not_found_msg)
            return False, not_found_msg

        except Exception as e:
            error_msg = f"❌ Unexpected error occurred: {str(e)}"
            print(error_msg)
            return False, error_msg
