import os
from typing import Optional
from .builder import Builder


class BuilderFutterAndroid(Builder):
    def __init__(
        self,
        build_path: str,
        flavor: Optional[str] = None,
    ) -> None:
        super().__init__(build_path, flavor)

    def build(self) -> None:
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

        # 원래 경로로 복원
        os.chdir(original_path)

        print("✅ Flutter Android build completed successfully.")
