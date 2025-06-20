import os
import re
import subprocess
from typing import Optional
from .builder import Builder


class BuilderFutterIOS(Builder):
    def __init__(
        self,
        build_path: str,
        flavor: Optional[str] = None,
        provisioning_profile: Optional[str] = None,
    ) -> None:
        super().__init__(build_path, flavor)
        self.provisioning_profile = provisioning_profile

    def build(self) -> str:
        print("=" * 80)
        print(
            f"🚀 Building iOS project at {self.build_path} with flavor {self.flavor}..."
        )
        # 현재 작업 디렉토리 저장
        original_path = os.getcwd()

        # 빌드 경로가 존재하는지 확인
        if not os.path.exists(self.build_path):
            raise FileNotFoundError(f"The build path {self.build_path} does not exist.")

        # 빌드 경로로 이동
        os.chdir(self.build_path)
        print(f"ℹ️  Changed working directory to {os.getcwd()}")

        # Bundle ID 가져오기
        bundle_id = self.get_bundle_id(scheme=self.flavor)
        if not bundle_id:
            raise ValueError(
                "Failed to get Bundle ID. Please check your Xcode project settings."
            )

        # Flutter 빌드 명령어 실행
        output = self.build_flutter(flavor=self.flavor)
        xcarchive_path = self.extract_xcarchive_path(output)
        if not xcarchive_path:
            raise ValueError(
                "Failed to extract xcarchive path from Flutter build output."
            )

        # Export iPA
        export_ipa_path = self.export_ipa(
            original_path=original_path,
            workspace=f"{os.getcwd()}/ios/Runner.xcworkspace",
            scheme=self.flavor,
            archive_path=xcarchive_path,
            output_directory=f"{os.path.dirname(xcarchive_path)}",
            bundle_id=bundle_id,
            provisioning_profile=self.provisioning_profile,
        )
        if not export_ipa_path:
            raise ValueError("Failed to export IPA file.")

        # 원래 경로로 복원
        os.chdir(original_path)
        print(f"ℹ️  Changed working directory to {os.getcwd()}")

        # 빌드 완료 메시지
        print("✅ Flutter iOS build completed successfully.")

        return export_ipa_path

    def build_flutter(self, flavor: str) -> Optional[str]:
        try:
            # 기본 명령어
            cmd = ["flutter", "build", "ipa"]

            # 파라미터 추가
            if flavor:
                cmd.append(f"--flavor")
                cmd.append(f"{flavor}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            stdout = result.stdout
            stderr = result.stderr
            full_output = stdout + stderr
            print(f"ℹ️  Flutter build Result:\n{full_output}")
            print("✅ Flutter build successfully.")
            return full_output
        except subprocess.CalledProcessError as e:
            full_output = e.stdout + e.stderr
            print(f"❌ Flutter build failed:\n{full_output}")
            return None

    def extract_xcarchive_path(self, output) -> Optional[str]:
        """Flutter 빌드 출력에서 xcarchive 경로 추출"""
        try:
            match = re.search(r"open\s+(.+\.xcarchive)", output, re.MULTILINE)
            if match:
                path = match.group(1).strip()
                print(f"ℹ️  Extract xcarchive path: {path}")
                return path
            return None
        except Exception as e:
            print(f"❌ Extract xcarchive path failed: {e}")
            return None

    def export_ipa(
        self,
        original_path: str,
        workspace: Optional[str] = None,
        scheme: Optional[str] = None,
        archive_path: Optional[str] = None,
        output_directory: Optional[str] = None,
        bundle_id: Optional[str] = None,
        provisioning_profile: Optional[str] = None,
    ) -> Optional[str]:
        """Export the xcarchive to an IPA file."""
        # 경로 변경
        fastlane_run_path = f"{original_path}/src"
        os.chdir(fastlane_run_path)
        print(f"ℹ️  Changed working directory to {os.getcwd()}")

        # 기본 명령어
        cmd = ["fastlane", "export"]

        # 파라미터 추가
        if workspace:
            cmd.append(f"workspace:{workspace}")
        if scheme:
            cmd.append(f"scheme:{scheme}")
        if archive_path:
            cmd.append(f"archive_path:{archive_path}")
        if output_directory:
            cmd.append(f"output_directory:{output_directory}")
        if bundle_id:
            cmd.append(f"bundle_id:{bundle_id}")
        if provisioning_profile:
            cmd.append(f"provisioning_profile:{provisioning_profile}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            stdout = result.stdout
            stderr = result.stderr
            full_output = stdout + stderr
            print(f"ℹ️  IPA export Result:\n{full_output}")
            print("✅ IPA export successfully.")

            def get_ipa_path(log_output):
                """fastlane 로그에서 IPA 파일 경로 추출"""
                pattern = r"([/\w\-_.]+\.ipa)"
                match = re.search(pattern, log_output)
                return match.group(1) if match else None

            return get_ipa_path(full_output)

        except subprocess.CalledProcessError as e:
            full_output = e.stdout + e.stderr
            print(f"❌ IPA export failed:\n{full_output}")
            return None

    def get_bundle_id(self, scheme: Optional[str] = None) -> Optional[str]:
        """xcodebuild로 Bundle ID 가져오기"""
        try:
            # 기본 명령어
            cmd = [
                "xcodebuild",
                "-showBuildSettings",
                "-workspace",
                "ios/Runner.xcworkspace",
                "-scheme",
                scheme if scheme else "Runner",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            # 정확한 패턴: 줄 시작 + 공백들 + PRODUCT_BUNDLE_IDENTIFIER + 공백 + = + 공백 + 값
            match = re.search(
                r"^\s*PRODUCT_BUNDLE_IDENTIFIER\s*=\s*(.+)$",
                result.stdout,
                re.MULTILINE,
            )
            if match:
                bundle_id = match.group(1).strip()
                print(f"✅ Get Bundle ID '{bundle_id}' successfully.")
                return bundle_id
            return None

        except subprocess.CalledProcessError as e:
            full_output = e.stdout + e.stderr
            print(f"❌ Get Bundle ID failed:\n{full_output}")
            return None
