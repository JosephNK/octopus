import subprocess
import json
from typing import Dict
from .deploy import Deploy, FastlaneRelease


class DeployAppStore(Deploy):
    def __init__(
        self,
        lane: FastlaneRelease,
        ipa_path: str,
        api_key_id: str,
        api_key_issuer_id: str,
        api_key_path: str,
        skip_binary_upload: bool = True,
        release_notes: Dict[str, str] = None,
    ):
        # Pass all parameters to parent class
        super().__init__(
            lane=lane,
            ipa_path=ipa_path,
            api_key_id=api_key_id,
            api_key_issuer_id=api_key_issuer_id,
            api_key_path=api_key_path,
            skip_binary_upload=skip_binary_upload,
            release_notes=release_notes or {"ko": "Bug fixes and improvements"},
        )

        # Set instance variables for easy access
        self.ipa_path = ipa_path
        self.api_key_id = api_key_id
        self.api_key_issuer_id = api_key_issuer_id
        self.api_key_path = api_key_path
        self.skip_binary_upload = skip_binary_upload
        self.release_notes = release_notes or {"ko": "Bug fixes and improvements"}

    def deploy(self):
        super().deploy()

        # Logic to deploy the app store
        print("🚀 Starting App Store deployment...")
        print(f"📁 IPA path: {self.ipa_path}")

        # Fastlane deployment command
        fastlane_cmd = [
            "fastlane",
            self.lane.value,
            f"ipa:{self.ipa_path}",
            f"api_key_id:{self.api_key_id}",
            f"api_key_issuer_id:{self.api_key_issuer_id}",
            f"api_key_path:{self.api_key_path}",
            f"skip_binary_upload:{str(self.skip_binary_upload).lower()}",
            f"release_notes:{json.dumps(self.release_notes, ensure_ascii=False)}",
        ]

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
