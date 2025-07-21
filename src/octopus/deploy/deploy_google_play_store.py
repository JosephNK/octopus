import subprocess

from pathlib import Path
from typing import Dict
from .deploy import Deploy, FastlaneRelease


class DeployGooglePlayStore(Deploy):
    def __init__(
        self,
        lane: FastlaneRelease,
        file_path: str,
        json_key_path: str,
        package_name: str,
        skip_upload_apk: bool = False,
        skip_upload_aab: bool = False,
        validate_only: bool = False,
        release_notes: Dict[str, str] = None,
    ):
        # Pass all parameters to parent class
        super().__init__(lane=lane)

        # Set instance variables for easy access
        self.file_path = file_path
        self.json_key_path = json_key_path
        self.package_name = package_name
        self.skip_upload_apk = skip_upload_apk
        self.skip_upload_aab = skip_upload_aab
        self.validate_only = validate_only
        self.release_notes = release_notes or {"ko": "Bug fixes and improvements"}

    def deploy(self):
        # Logic to deploy the app store
        print("🚀 Starting App Store deployment...")
        print(f"📁 APK or AAB path: {self.file_path}")

        build_path = Path(self.file_path)
        file_ext = build_path.suffix  # .apk or .aab

        # Fastlane deployment command
        fastlane_cmd = [
            "fastlane",
            "android",
            self.lane.value,
            # f"release_notes:{json.dumps(self.release_notes, ensure_ascii=False)}",
        ]
        if file_ext == ".apk":
            fastlane_cmd.append(f"apk:{self.file_path}")
        elif file_ext == ".aab":
            fastlane_cmd.append(f"aab:{self.file_path}")
        fastlane_cmd.append(f"json_key:{self.json_key_path}")
        fastlane_cmd.append(f"package_name:{self.package_name}")
        fastlane_cmd.append(f"skip_upload_apk:{str(self.skip_upload_apk).lower()}")
        fastlane_cmd.append(f"skip_upload_aab:{str(self.skip_upload_aab).lower()}")
        fastlane_cmd.append(f"validate_only:{str(self.validate_only).lower()}")

        try:
            print("⏳ Running fastlane deployment...")
            result = subprocess.run(
                fastlane_cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            print("✅ Fastlane deployment successful!")
            if result.stdout:
                print("📝 Output:")
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Fastlane deployment failed!")
            print(f"🔍 Error details: {e}")
            if e.stderr:
                print("📄 Error output:")
                print(e.stderr)
            return False
