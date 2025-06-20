import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


class FlutterMainFinder:
    """
    A class to find main() functions in Flutter projects
    """

    def __init__(self, search_path: str = ".", recursive_search: bool = True):
        """
        Initialize FlutterMainFinder

        Args:
            search_path (str): Path to start searching from
            recursive_search (bool): Whether to recursively search subdirectories for Flutter projects
        """
        self.search_path = Path(search_path).resolve()
        self.recursive_search = recursive_search
        self.flutter_projects = []
        self.main_files = []

        # Regular expression patterns for finding main() functions
        self.main_patterns = [
            r"void\s+main\s*\(",  # void main(
            r"Future<void>\s+main\s*\(",  # Future<void> main(
            r"main\s*\(",  # main(
        ]

        # Regular expression patterns for runApp() functions
        self.runapp_patterns = [
            r"runApp\s*\(",  # runApp(
            r"flutter\.runApp\s*\(",  # flutter.runApp(
        ]

        # Directories to search in
        self.search_dirs = ["lib", "test"]

    def find_flutter_projects(self) -> List[Path]:
        """
        Find Flutter projects in the specified path

        Returns:
            List[Path]: List of discovered Flutter project paths
        """
        flutter_projects = []

        if not self.search_path.exists():
            print(f"❌ Search path does not exist: {self.search_path}")
            return flutter_projects

        print("=" * 80)
        print(f"🔍 Searching for Flutter projects: {self.search_path}")

        if self.recursive_search:
            # Recursively find pubspec.yaml files
            for pubspec_file in self.search_path.rglob("pubspec.yaml"):
                project_path = pubspec_file.parent

                # Check if it's a Flutter project (has flutter dependencies in pubspec.yaml)
                if self.is_flutter_project_at_path(project_path):
                    flutter_projects.append(project_path)
                    print(
                        f"✅ Flutter project found: {project_path.relative_to(self.search_path)}"
                    )
        else:
            # Check only current path
            if self.is_flutter_project_at_path(self.search_path):
                flutter_projects.append(self.search_path)
                print(f"✅ Flutter project confirmed: {self.search_path}")

        self.flutter_projects = flutter_projects
        return flutter_projects

    def is_flutter_project_at_path(self, project_path: Path) -> bool:
        """
        Check if the specified path is a Flutter project

        Args:
            project_path (Path): Project path to check

        Returns:
            bool: Whether it's a Flutter project
        """
        pubspec_file = project_path / "pubspec.yaml"
        if not pubspec_file.exists():
            return False

        try:
            # Read pubspec.yaml file and check for flutter dependencies
            with open(pubspec_file, "r", encoding="utf-8") as f:
                content = f.read().lower()
                # Check if flutter SDK or flutter dependencies exist
                return (
                    "flutter:" in content
                    or "flutter_test:" in content
                    or "sdk: flutter" in content
                )
        except Exception:
            # If file can't be read, judge by pubspec.yaml existence only
            return True

    def validate_search_path(self) -> bool:
        """
        Validate search path

        Returns:
            bool: Whether the search path is valid
        """
        if not self.search_path.exists():
            print(f"❌ Search path does not exist: {self.search_path}")
            return False
        return True

    def search_main_in_file(
        self, dart_file: Path, project_path: Path
    ) -> Optional[Dict]:
        """
        Search for main() function and runApp() call in a single .dart file

        Args:
            dart_file (Path): .dart file path to search
            project_path (Path): Root path of the corresponding Flutter project

        Returns:
            Optional[Dict]: main() function information or None
        """
        try:
            with open(dart_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Search for main() function patterns
            main_pattern_found = None
            for pattern in self.main_patterns:
                if re.search(pattern, content):
                    main_pattern_found = pattern
                    break

            if not main_pattern_found:
                return None

            # Check for runApp() function call
            has_runapp = False
            runapp_pattern_found = None
            for pattern in self.runapp_patterns:
                if re.search(pattern, content):
                    has_runapp = True
                    runapp_pattern_found = pattern
                    break

            relative_to_search = dart_file.relative_to(self.search_path)
            relative_to_project = dart_file.relative_to(project_path)

            return {
                "file": str(relative_to_search),
                "project_file": str(relative_to_project),
                "project_path": str(project_path),
                "absolute_path": str(dart_file),
                "main_pattern_matched": main_pattern_found,
                "has_runapp": has_runapp,
                "runapp_pattern_matched": runapp_pattern_found,
                "content": content,
                "is_flutter_entry_point": has_runapp,  # If runApp exists, it's an actual Flutter entry point
            }

        except Exception as e:
            print(f"⚠️  File reading error {dart_file}: {e}")

        return None

    def find_main_functions(self) -> List[Dict]:
        """
        Search for all main() functions in Flutter projects

        Returns:
            List[Dict]: List of file information containing main() functions
        """
        if not self.validate_search_path():
            return []

        # Find Flutter projects
        flutter_projects = self.find_flutter_projects()

        if not flutter_projects:
            print("❌ No Flutter projects found.")
            return []

        self.main_files = []

        # Search for main() functions in each Flutter project
        for project_path in flutter_projects:
            print(
                f"🔍 Searching for main() functions in {project_path.relative_to(self.search_path)}..."
            )

            # Search .dart files in each search directory
            for search_dir in self.search_dirs:
                dir_path = project_path / search_dir
                if not dir_path.exists():
                    continue

                # Recursively search .dart files
                for dart_file in dir_path.rglob("*.dart"):
                    main_info = self.search_main_in_file(dart_file, project_path)
                    if main_info:
                        self.main_files.append(main_info)
                        entry_type = (
                            "Flutter app entry point"
                            if main_info["has_runapp"]
                            else "main() function"
                        )
                        print(f"✅ {entry_type} found: {main_info['file']}")

        return self.main_files

    def get_flutter_entry_points(self) -> List[Dict]:
        """
        Return only actual Flutter app entry points (main() functions with runApp)

        Returns:
            List[Dict]: Flutter app entry point files
        """
        return [f for f in self.main_files if f["has_runapp"]]
