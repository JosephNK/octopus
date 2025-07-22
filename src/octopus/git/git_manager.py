import os
import re
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

    @staticmethod
    def get_repo_name(url):
        match = re.search(r"/([^/]+?)(?:\.git)?/?$", url)
        return match.group(1) if match else None

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

    def remove_directory(self) -> bool:
        """
        Remove local directory

        Returns:
            bool: Success status
        """
        try:
            if self.local_path.exists():
                shutil.rmtree(self.local_path)
                print(f"🗑️  Directory removed: {self.local_path}")
                return True
            else:
                print(f"ℹ️  Directory does not exist: {self.local_path}")
                return True
        except Exception as e:
            print(f"❌ Failed to remove directory: {e}")
            return False

    def clone_repository(self) -> bool:
        """
        Clone Git repository

        Returns:
            bool: Success status
        """
        command = ["git", "clone", self.repo_url, str(self.local_path)]
        success, output = self._run_command(command)

        if success:
            print(f"📥 Repository cloned: {self.repo_url} -> {self.local_path}")
            return True
        else:
            print(f"❌ Clone failed: {output}")
            return False

    def pull_repository(self) -> bool:
        """
        Pull latest changes from Git repository

        Returns:
            bool: Success status
        """
        if not self._is_git_repo():
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        command = ["git", "pull"]
        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"📥 Pull completed: {output.strip()}")
            return True
        else:
            print(f"❌ Pull failed: {output}")
            return False

    def fresh_pull(self) -> bool:
        """
        Remove existing folder and clone fresh

        Returns:
            bool: Success status
        """
        print(f"🔄 Starting fresh pull: {self.repo_url}")

        # 1. Remove existing directory
        if not self.remove_directory():
            return False

        # 2. Clone fresh
        if not self.clone_repository():
            return False

        print("✅ Fresh pull completed!")
        return True

    def sync_repository(self, force_fresh: bool = False) -> bool:
        """
        Synchronize repository (pull or fresh pull)

        Args:
            force_fresh (bool): Force fresh pull execution

        Returns:
            bool: Success status
        """
        if force_fresh:
            return self.fresh_pull()

        # If local path exists and is a Git repository, pull
        if self.local_path.exists() and self._is_git_repo():
            return self.pull_repository()
        else:
            # If doesn't exist or not a Git repository, fresh pull
            return self.fresh_pull()

    def delete_branch(
        self, branch_name: str, force: bool = False, remote: bool = False
    ) -> bool:
        """
        Delete branch

        Args:
            branch_name (str): Branch name to delete
            force (bool): Force delete (delete unmerged branches)
            remote (bool): Also delete remote branch

        Returns:
            bool: Success status
        """
        if not self._is_git_repo():
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        success = True

        # Check current branch
        current_success, current_branch = self._run_command(
            ["git", "branch", "--show-current"], cwd=str(self.local_path)
        )

        if current_success and current_branch.strip() == branch_name:
            print(
                f"❌ Cannot delete current branch ({branch_name}). Please switch to another branch first."
            )
            return False

        # Delete local branch
        delete_option = "-D" if force else "-d"
        command = ["git", "branch", delete_option, branch_name]
        local_success, output = self._run_command(command, cwd=str(self.local_path))

        if local_success:
            print(f"🗑️  Local branch deleted: {branch_name}")
        else:
            print(f"❌ Local branch deletion failed: {output}")
            success = False

        # Delete remote branch
        if remote and local_success:
            remote_command = ["git", "push", "origin", "--delete", branch_name]
            remote_success, remote_output = self._run_command(
                remote_command, cwd=str(self.local_path)
            )

            if remote_success:
                print(f"🌐 Remote branch deleted: origin/{branch_name}")
            else:
                print(f"❌ Remote branch deletion failed: {remote_output}")
                success = False

        return success

    def _checkout_with_strategy(
        self, target: str, target_type: str, strategy: str = "fresh"
    ) -> bool:
        """
        공통 체크아웃 로직 (strategy 지원)

        Args:
            target (str): 체크아웃 대상 (브랜치명, 커밋해시, 태그명)
            target_type (str): 대상 타입 ("branch", "commit", "tag")
            strategy (str): 체크아웃 전략
                - "fresh": 완전 새로 클론 (기존 폴더 삭제 → 클론 → 체크아웃)
                - "preserve": 기존 저장소 보존 시도 (로컬 정리 → 체크아웃, 불가능하면 새로 클론)

        Returns:
            bool: Success status
        """
        print("=" * 80)
        emoji_map = {"branch": "🌿", "commit": "📌", "tag": "🏷️"}
        emoji = emoji_map.get(target_type, "🔀")
        print(f"🚀 Starting {target_type} checkout: {target}")

        # Strategy 검증
        if strategy not in ["fresh", "preserve"]:
            print(f"❌ Invalid strategy: {strategy}. Use 'fresh' or 'preserve'")
            return False

        if strategy == "preserve":
            # Strategy 1: 기존 저장소 보존 시도
            print(
                "🧹 Using preserve strategy (attempting to keep existing repository)..."
            )

            # 1. 로컬 경로가 없으면 클론부터 시작
            if not self.local_path.exists():
                print(f"ℹ️  Local path does not exist, cloning first: {self.local_path}")
                if not self.clone_repository():
                    return False

            # 2. Git 저장소가 아니면 새로 클론
            elif not self._is_git_repo():
                print(f"ℹ️  Not a Git repository, removing and cloning fresh...")
                if not self.remove_directory() or not self.clone_repository():
                    return False

            # 3. 기존 저장소가 있다면 정리 과정 진행
            else:
                print("ℹ️  Existing Git repository found, cleaning up...")

                # Reset local changes
                print("🔄 Resetting local changes...")
                if not self.reset_hard():
                    return False

                # Clean untracked files
                print("🧹 Cleaning untracked files...")
                if not self.clean_untracked():
                    return False

                # Fetch latest changes (브랜치의 경우만)
                if target_type == "branch":
                    print("📥 Fetching latest changes...")
                    fetch_success, fetch_output = self._run_command(
                        ["git", "fetch"], cwd=str(self.local_path)
                    )
                    if not fetch_success:
                        print(f"❌ Fetch failed: {fetch_output}")
                        return False

            # 4. 현재 상태 확인 및 체크아웃
            needs_checkout = True

            if target_type == "branch":
                current_success, current_branch = self._run_command(
                    ["git", "branch", "--show-current"], cwd=str(self.local_path)
                )
                needs_checkout = not (
                    current_success and current_branch.strip() == target
                )

            if needs_checkout:
                print(f"{emoji} Checking out to {target_type}: {target}")

                # 체크아웃 명령어 구성
                if target_type == "tag":
                    command = ["git", "checkout", f"tags/{target}"]
                else:
                    command = ["git", "checkout", target]

                success, output = self._run_command(command, cwd=str(self.local_path))

                if not success:
                    print(f"❌ {target_type.capitalize()} checkout failed: {output}")
                    return False

                print(
                    f"{emoji} {target_type.capitalize()} checkout completed: {target}"
                )
            else:
                print(f"ℹ️  Already on {target_type}: {target}, updating to latest...")

            # 5. 최신 변경사항 풀 (브랜치의 경우만)
            if target_type == "branch" and not needs_checkout:
                print("📥 Pulling latest changes...")
                if self.pull_repository():
                    print("✅ Preserve strategy checkout completed!")
                    return True
                else:
                    print("⚠️  Checkout successful but pull failed")
                    return True  # Return True since checkout was successful
            else:
                print("✅ Preserve strategy checkout completed!")
                return True

        else:
            # Strategy 2: Fresh clone (기존 로직)
            print("🗑️  Using fresh strategy (remove → clone → checkout)...")

            # 1. Remove existing directory
            if not self.remove_directory():
                return False

            # 2. Clone fresh
            if not self.clone_repository():
                return False

            # 3. Checkout specific target
            print(f"{emoji} Checking out to {target_type}: {target}")

            # 체크아웃 명령어 구성
            if target_type == "tag":
                command = ["git", "checkout", f"tags/{target}"]
            else:
                command = ["git", "checkout", target]

            success, output = self._run_command(command, cwd=str(self.local_path))

            if success:
                print(
                    f"{emoji} {target_type.capitalize()} checkout completed: {target}"
                )
                print("✅ Fresh strategy checkout completed!")
                return True
            else:
                print(f"❌ {target_type.capitalize()} checkout failed: {output}")
                return False

    def checkout_branch(self, branch_name: str, strategy: str = "fresh") -> bool:
        """
        Checkout to specific branch

        Args:
            branch_name (str): Branch name to checkout
            strategy (str): Checkout strategy
                - "fresh": 완전 새로 클론 (기존 폴더 삭제 → 클론 → 체크아웃)
                - "preserve": 기존 저장소 보존 시도 (로컬 정리 → 체크아웃, 불가능하면 새로 클론)

        Returns:
            bool: Success status
        """
        return self._checkout_with_strategy(branch_name, "branch", strategy)

    def checkout_commit(self, commit_hash: str, strategy: str = "fresh") -> bool:
        """
        Checkout specific commit

        Args:
            commit_hash (str): Commit hash
            strategy (str): Checkout strategy
                - "fresh": 완전 새로 클론 (기존 폴더 삭제 → 클론 → 체크아웃)
                - "preserve": 기존 저장소 보존 시도 (로컬 정리 → 체크아웃, 불가능하면 새로 클론)

        Returns:
            bool: Success status
        """
        if not self._is_git_repo() and strategy == "preserve":
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        return self._checkout_with_strategy(commit_hash, "commit", strategy)

    def checkout_tag(self, tag_name: str, strategy: str = "fresh") -> bool:
        """
        Checkout specific tag

        Args:
            tag_name (str): Tag name to checkout
            strategy (str): Checkout strategy
                - "fresh": 완전 새로 클론 (기존 폴더 삭제 → 클론 → 체크아웃)
                - "preserve": 기존 저장소 보존 시도 (로컬 정리 → 체크아웃, 불가능하면 새로 클론)

        Returns:
            bool: Success status
        """
        if not self._is_git_repo() and strategy == "preserve":
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        return self._checkout_with_strategy(tag_name, "tag", strategy)

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
            "local_path": str(self.local_path),
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

    def reset_hard(self, target: str = "HEAD") -> bool:
        """
        Execute git reset --hard (delete all local changes)

        Args:
            target (str): Reset target (default: HEAD)

        Returns:
            bool: Success status
        """
        if not self._is_git_repo():
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        command = ["git", "reset", "--hard", target]
        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"🔄 Hard reset completed: {target}")
            return True
        else:
            print(f"❌ Hard reset failed: {output}")
            return False

    def clean_untracked(self, force: bool = True, directories: bool = True) -> bool:
        """
        Delete untracked files and directories

        Args:
            force (bool): Force deletion
            directories (bool): Also delete directories

        Returns:
            bool: Success status
        """
        if not self._is_git_repo():
            print(f"❌ Not a Git repository: {self.local_path}")
            return False

        command = ["git", "clean"]
        if force:
            command.append("-f")
        if directories:
            command.append("-d")

        success, output = self._run_command(command, cwd=str(self.local_path))

        if success:
            print(f"🧹 Untracked files/directories cleaned")
            if output.strip():
                print(f"Deleted items:\n{output}".strip())
            return True
        else:
            print(f"❌ Clean failed: {output}")
            return False
