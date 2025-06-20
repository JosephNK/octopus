import os
import re
import subprocess
from typing import Optional
from .builder import Builder


class BuilderFutterAndroid(Builder):
    def __init__(
        self,
        build_path: str,
        flavor: Optional[str] = None,
        use_appbundle: bool = True,
    ) -> None:
        super().__init__(build_path, flavor)
        self.use_appbundle = use_appbundle

    def build(self) -> str:
        print("=" * 80)
        print(
            f"🚀 Building Android project at {self.build_path} with flavor {self.flavor}..."
        )
        # 현재 작업 디렉토리 저장
        original_path = os.getcwd()

        # 빌드 경로가 존재하는지 확인
        if not os.path.exists(self.build_path):
            raise FileNotFoundError(f"The build path {self.build_path} does not exist.")

        # 빌드 경로로 이동
        os.chdir(self.build_path)
        print(f"ℹ️  Changed working build directory to {os.getcwd()}")

        # Flutter 빌드 명령어 실행
        output = self.build_flutter(flavor=self.flavor)
        extract_path = self.extract_file_path(output)
        if not extract_path:
            raise ValueError("Failed to extract path from Flutter build output.")

        # 원래 경로로 복원
        os.chdir(original_path)
        print(f"ℹ️  Changed working original directory to {os.getcwd()}")

        # 빌드 완료 메시지
        print("✅ Flutter Android build completed successfully.")

        return f"{original_path}/{self.build_path}/{extract_path}"

    def build_flutter(self, flavor: str) -> Optional[str]:
        try:
            print("ℹ️  Running build flutter...")

            if self.use_appbundle:
                cmd = ["flutter", "build", "appbundle"]
            else:
                cmd = ["flutter", "build", "apk"]

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
            print(f"{full_output}")
            print("✅ Flutter build successfully.")
            return full_output
        except subprocess.CalledProcessError as e:
            full_output = e.stdout + e.stderr
            print(f"❌ Flutter build failed:\n{full_output}")
            return None

    def extract_file_path(self, build_output: str) -> Optional[str]:
        """
        Gradle 빌드 출력 텍스트에서 AAB/APK 파일 경로를 추출하는 함수

        Args:
            build_output (str): Gradle 빌드 출력 텍스트

        Returns:
            str: 추출된 파일 경로 (없으면 None)
        """

        # Built 다음에 오는 .aab 파일 (✓, !, >, * 등 다양한 기호 고려)
        aab_pattern = r"Built\s+([^\s]+\.aab)"
        aab_match = re.search(aab_pattern, build_output)

        if aab_match:
            return aab_match.group(1)

        # Built 다음에 오는 .apk 파일 (✓, !, >, * 등 다양한 기호 고려)
        apk_pattern = r"Built\s+([^\s]+\.apk)"
        apk_match = re.search(apk_pattern, build_output)

        if apk_match:
            return apk_match.group(1)

        # build/ 경로가 포함된 .aab/.apk 파일
        build_path_pattern = r"(build/[^\s]*\.(aab|apk))"
        build_match = re.search(build_path_pattern, build_output)

        if build_match:
            return build_match.group(1)

        # app-release.aab 또는 app-release.apk 형태 (경로 포함)
        file_pattern = r"([^\s]*app-release\.(aab|apk))"
        file_match = re.search(file_pattern, build_output)

        if file_match:
            return file_match.group(1)

        # 일반적인 .aab/.apk 파일 패턴 (마지막 수단)
        general_pattern = r"([^\s]+\.(aab|apk))"
        general_match = re.search(general_pattern, build_output)

        if general_match:
            return general_match.group(1)

        return None
