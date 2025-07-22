import subprocess
import json
from typing import Dict, Optional
from .deploy import Deploy, FastlaneRelease


class DeployAppStore(Deploy):
    def __init__(
        self,
        lane: FastlaneRelease,
        file_path: str,
        api_key_id: str,
        api_key_issuer_id: str,
        api_key_path: str,
        groups: Optional[str] = None,
        release_notes: Dict[str, str] = None,
    ):
        # Pass all parameters to parent class
        super().__init__(lane=lane)

        # Set instance variables for easy access
        self.file_path = file_path
        self.api_key_id = api_key_id
        self.api_key_issuer_id = api_key_issuer_id
        self.api_key_path = api_key_path
        self.groups = groups
        self.release_notes = release_notes or {"ko": "Bug fixes and improvements"}

    def deploy(self):
        super().deploy()

        # Logic to deploy the app store
        print("🚀 Starting App Store deployment...")
        print(f"📁 IPA path: {self.file_path}")

        # Fastlane command to print build info
        fastlane_cmd_print = [
            "fastlane",
            "ios",
            "print_build_info",
            f"ipa:{self.file_path}",
        ]
        subprocess.run(fastlane_cmd_print, check=True, text=True)

        # Fastlane deployment command
        fastlane_cmd = [
            "fastlane",
            "ios",
            self.lane.value,
            f"ipa:{self.file_path}",
            f"api_key_id:{self.api_key_id}",
            f"api_key_issuer_id:{self.api_key_issuer_id}",
            f"api_key_path:{self.api_key_path}",
        ]
        if self.release_notes:
            fastlane_cmd.append(
                f"release_notes:{json.dumps(self.release_notes, ensure_ascii=False)}"
            )
        if self.groups:
            fastlane_cmd.append(f"groups:{self.groups}")

        try:
            print("⏳ Running fastlane deployment...")
            subprocess.run(fastlane_cmd, check=True, text=True)
            print("✅ Fastlane deployment successful!")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Fastlane deployment failed!")
            print(f"🔍 Error details: {e}")
            if e.stderr:
                print("📄 Error output:")
                print(e.stderr)
            return False
