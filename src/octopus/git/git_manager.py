import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class GitManager:
    """Git 저장소를 관리하는 클래스"""

    def __init__(self, repo_url: str, local_path: str):
        """
        GitManager 초기화

        Args:
            repo_url (str): Git 저장소 URL
            local_path (str): 로컬 저장 경로
        """
        self.repo_url = repo_url
        self.local_path = Path(local_path)

    def remove_directory(self) -> bool:
        """
        로컬 디렉토리를 삭제

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.local_path.exists():
                shutil.rmtree(self.local_path)
                print(f"디렉토리 삭제 완료: {self.local_path}")
                return True
            else:
                print(f"디렉토리가 존재하지 않음: {self.local_path}")
                return True
        except Exception as e:
            print(f"디렉토리 삭제 실패: {e}")
            return False

    def clone_repository(self) -> bool:
        """
        Git 저장소를 클론

        Returns:
            bool: 클론 성공 여부
        """
        command = ["git", "clone", self.repo_url, str(self.local_path)]
        success, output = self._run_command(command)

        if success:
            print(f"저장소 클론 완료: {self.repo_url} -> {self.local_path}")
            return True
        else:
            print(f"저장소 클론 실패: {output}")
            return False

    def pull_repository(self) -> bool:
        """
        Git 저장소에서 최신 변경사항을 pull

        Returns:
            bool: Pull 성공 여부
        """
        if not self._is_git_repo():
            print(f"Git 저장소가 아닙니다: {self.local_path}")
            return False

        command = ["git", "pull"]
        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"Pull 완료: {output.strip()}")
            return True
        else:
            print(f"Pull 실패: {output}")
            return False

    def fresh_pull(self) -> bool:
        """
        폴더가 존재하면 삭제 후 새로 클론

        Returns:
            bool: 작업 성공 여부
        """
        print(f"Fresh pull 시작: {self.repo_url}")

        # 1. 기존 디렉토리 삭제
        if not self.remove_directory():
            return False

        # 2. 새로 클론
        if not self.clone_repository():
            return False

        print("Fresh pull 완료!")
        return True

    def sync_repository(self, force_fresh: bool = False) -> bool:
        """
        저장소를 동기화 (pull 또는 fresh pull)

        Args:
            force_fresh (bool): 강제로 fresh pull 실행 여부

        Returns:
            bool: 동기화 성공 여부
        """
        if force_fresh:
            return self.fresh_pull()

        # 로컬 경로가 존재하고 Git 저장소인 경우 pull
        if self.local_path.exists() and self._is_git_repo():
            return self.pull_repository()
        else:
            # 존재하지 않거나 Git 저장소가 아닌 경우 fresh pull
            return self.fresh_pull()

    def checkout_branch(self, branch_name: str, create_new: bool = False) -> bool:
        """
        브랜치를 체크아웃

        Args:
            branch_name (str): 체크아웃할 브랜치 이름
            create_new (bool): 새 브랜치 생성 여부

        Returns:
            bool: 체크아웃 성공 여부
        """
        if not self._is_git_repo():
            print(f"Git 저장소가 아닙니다: {self.local_path}")
            return False

        if create_new:
            command = ["git", "checkout", "-b", branch_name]
            action = f"새 브랜치 생성 및 체크아웃: {branch_name}"
        else:
            command = ["git", "checkout", branch_name]
            action = f"브랜치 체크아웃: {branch_name}"

        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"{action} 완료")
            return True
        else:
            print(f"{action} 실패: {output}")
            return False

    def checkout_commit(self, commit_hash: str) -> bool:
        """
        특정 커밋을 체크아웃

        Args:
            commit_hash (str): 커밋 해시

        Returns:
            bool: 체크아웃 성공 여부
        """
        if not self._is_git_repo():
            print(f"Git 저장소가 아닙니다: {self.local_path}")
            return False

        command = ["git", "checkout", commit_hash]
        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"커밋 체크아웃 완료: {commit_hash}")
            return True
        else:
            print(f"커밋 체크아웃 실패: {output}")
            return False

    def get_branches(self) -> tuple[bool, list]:
        """
        모든 브랜치 목록 반환

        Returns:
            tuple[bool, list]: (성공 여부, 브랜치 목록)
        """
        if not self._is_git_repo():
            return False, []

        # 로컬 브랜치
        success, local_output = self._run_command(
            ["git", "branch"], cwd=str(self.local_path)
        )

        # 원격 브랜치
        remote_success, remote_output = self._run_command(
            ["git", "branch", "-r"], cwd=str(self.local_path)
        )

        branches = {"local": [], "remote": [], "current": None}

        if success:
            for line in local_output.strip().split("\n"):
                line = line.strip()
                if line.startswith("* "):
                    branches["current"] = line[2:]  # 현재 브랜치 (*)
                    branches["local"].append(line[2:])
                elif line:
                    branches["local"].append(line)

        if remote_success:
            for line in remote_output.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("origin/HEAD"):
                    branches["remote"].append(line)

        return True, branches

    def get_status(self) -> dict:
        """
        저장소 상태 정보 반환

        Returns:
            dict: 상태 정보
        """
        status = {
            "local_path_exists": self.local_path.exists(),
            "is_git_repo": False,
            "current_branch": None,
            "remote_url": None,
            "branches": None,
        }

        if status["local_path_exists"]:
            status["is_git_repo"] = self._is_git_repo()

            if status["is_git_repo"]:
                # 현재 브랜치 확인
                success, branch = self._run_command(
                    ["git", "branch", "--show-current"], cwd=str(self.local_path)
                )
                if success:
                    status["current_branch"] = branch.strip()

                # 원격 URL 확인
                success, url = self._run_command(
                    ["git", "remote", "get-url", "origin"], cwd=str(self.local_path)
                )
                if success:
                    status["remote_url"] = url.strip()

                # 브랜치 정보
                branches_success, branches = self.get_branches()
                if branches_success:
                    status["branches"] = branches

        return status

    def _run_command(
        self, command: list, cwd: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        명령어를 실행하고 결과를 반환

        Args:
            command (list): 실행할 명령어 리스트
            cwd (str, optional): 작업 디렉토리

        Returns:
            tuple[bool, str]: (성공 여부, 출력/에러 메시지)
        """
        try:
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e.stderr}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def _is_git_repo(self) -> bool:
        """
        해당 경로가 Git 저장소인지 확인

        Returns:
            bool: Git 저장소 여부
        """
        git_dir = self.local_path / ".git"
        return git_dir.exists()


# 사용 예시
# if __name__ == "__main__":
#     # GitManager 인스턴스 생성
#     git_manager = GitManager(
#         repo_url="https://github.com/username/repository.git", local_path="./my_project"
#     )

#     # 상태 확인
#     status = git_manager.get_status()
#     print("현재 상태:", status)

#     # 저장소 동기화
#     if git_manager.sync_repository():
#         print("동기화 성공!")
#     else:
#         print("동기화 실패!")

#     # 브랜치 목록 확인
#     success, branches = git_manager.get_branches()
#     if success:
#         print("브랜치 정보:")
#         print(f"  현재 브랜치: {branches['current']}")
#         print(f"  로컬 브랜치: {branches['local']}")
#         print(f"  원격 브랜치: {branches['remote']}")

# 브랜치 체크아웃
# git_manager.checkout_branch("develop")

# 새 브랜치 생성 및 체크아웃
# git_manager.checkout_branch("feature/new-feature", create_new=True)

# 특정 커밋 체크아웃
# git_manager.checkout_commit("a1b2c3d4")

# 강제로 fresh pull 실행
# git_manager.sync_repository(force_fresh=True)
