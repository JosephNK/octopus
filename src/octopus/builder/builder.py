from abc import ABC, abstractmethod
from typing import Optional


class Builder(ABC):
    def __init__(self, build_path: str, flavor: Optional[str] = None) -> None:
        self.build_path = build_path
        self.flavor = flavor
        pass

    @abstractmethod
    def build(self) -> None:
        """
        Build the project.
        This method should be implemented by subclasses to perform the actual build process.
        """
        raise NotImplementedError("Subclasses must implement this method.")
