from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class FastlaneRelease(Enum):
    DEV_RELEASE = "dev_release"
    AUTO_RELEASE = "auto_release"


class Deploy(ABC):
    def __init__(
        self, lane: FastlaneRelease = FastlaneRelease.DEV_RELEASE, **kwargs
    ) -> None:
        self.lane = lane
        self.config = kwargs

    @abstractmethod
    def deploy(self) -> Optional[bool]:
        """
        Deploy the project.
        This method should be implemented by subclasses to perform the actual deployment process.
        """
        import os

        # Change to src/fastlane directory
        fastlane_dir = "src/fastlane"
        if os.path.exists(fastlane_dir):
            os.chdir(fastlane_dir)
            print(f"✅ Successfully changed directory to: {os.getcwd()}")
        else:
            print(f"❌ Directory '{fastlane_dir}' does not exist")

        return False
