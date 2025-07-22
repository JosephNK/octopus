from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .git_manager import GitManager


class GitCheckoutManager:
    """Git 체크아웃 전용 관리 클래스"""

    def __init__(self, git_manager: "GitManager"):
        """
        GitCheckoutManager 초기화

        Args:
            git_manager: GitManager 인스턴스
        """
        self.git_manager = git_manager

    def _get_checkout_emoji(self, target_type: str) -> str:
        """체크아웃 타입에 맞는 이모지 반환"""
        emoji_map = {"branch": "🌿", "commit": "📌", "tag": "🏷️"}
        return emoji_map.get(target_type, "🔀")

    def _prepare_repository_for_preserve_strategy(self) -> bool:
        """Preserve 전략을 위한 저장소 준비"""
        # 1. 로컬 경로가 없으면 클론부터 시작
        if not self.git_manager.local_path.exists():
            print(
                f"ℹ️  Local path does not exist, cloning first: {self.git_manager.local_path}"
            )
            return self.git_manager.clone_repository()

        # 2. Git 저장소가 아니면 새로 클론
        if not self.git_manager._is_git_repo():
            print(f"ℹ️  Not a Git repository, removing and cloning fresh...")
            return (
                self.git_manager.remove_directory()
                and self.git_manager.clone_repository()
            )

        # 3. 기존 저장소가 있다면 정리 과정 진행
        print("ℹ️  Existing Git repository found, cleaning up...")
        return self._clean_existing_repository()

    def _clean_existing_repository(self) -> bool:
        """기존 저장소 정리"""
        print("🔄 Resetting local changes...")
        if not self.git_manager.reset_hard():
            return False

        print("🧹 Cleaning untracked files...")
        if not self.git_manager.clean_untracked():
            return False

        return True

    def _fetch_if_needed(self, target_type: str) -> bool:
        """필요한 경우 최신 변경사항 가져오기 (브랜치의 경우만)"""
        if target_type == "branch":
            print("📥 Fetching latest changes...")
            fetch_success, fetch_output = self.git_manager._run_command(
                ["git", "fetch"], cwd=str(self.git_manager.local_path)
            )
            if not fetch_success:
                print(f"❌ Fetch failed: {fetch_output}")
                return False
        return True

    def _is_already_on_target(self, target: str, target_type: str) -> bool:
        """현재 대상과 동일한지 확인"""
        if target_type == "branch":
            current_success, current_branch = self.git_manager._run_command(
                ["git", "branch", "--show-current"],
                cwd=str(self.git_manager.local_path),
            )
            return current_success and current_branch.strip() == target
        return False

    def _build_checkout_command(self, target: str, target_type: str) -> list:
        """체크아웃 명령어 구성"""
        if target_type == "tag":
            return ["git", "checkout", f"tags/{target}"]
        else:
            return ["git", "checkout", target]

    def _perform_checkout(self, target: str, target_type: str) -> bool:
        """실제 체크아웃 수행"""
        emoji = self._get_checkout_emoji(target_type)
        print(f"{emoji} Checking out to {target_type}: {target}")

        command = self._build_checkout_command(target, target_type)
        success, output = self.git_manager._run_command(
            command, cwd=str(self.git_manager.local_path)
        )

        if not success:
            print(f"❌ {target_type.capitalize()} checkout failed: {output}")
            return False

        print(f"{emoji} {target_type.capitalize()} checkout completed: {target}")
        return True

    def _handle_branch_update(self, target: str, needs_checkout: bool) -> bool:
        """브랜치의 경우 최신 변경사항 업데이트 처리"""
        if not needs_checkout:
            print("📥 Pulling latest changes...")
            if self.git_manager.pull_repository():
                print("✅ Preserve strategy checkout completed!")
                return True
            else:
                print("⚠️  Checkout successful but pull failed")
                return True  # Return True since checkout was successful
        else:
            print("✅ Preserve strategy checkout completed!")
            return True

    def _checkout_with_preserve_strategy(self, target: str, target_type: str) -> bool:
        """Preserve 전략으로 체크아웃 수행"""
        print("🧹 Using preserve strategy (attempting to keep existing repository)...")

        # 1. 저장소 준비
        if not self._prepare_repository_for_preserve_strategy():
            return False

        # 2. 필요시 fetch 수행
        if not self._fetch_if_needed(target_type):
            return False

        # 3. 현재 상태 확인 및 체크아웃
        already_on_target = self._is_already_on_target(target, target_type)

        if not already_on_target:
            if not self._perform_checkout(target, target_type):
                return False
        else:
            print(f"ℹ️  Already on {target_type}: {target}, updating to latest...")

        # 4. 브랜치의 경우 최신 변경사항 업데이트
        if target_type == "branch":
            return self._handle_branch_update(target, not already_on_target)
        else:
            print("✅ Preserve strategy checkout completed!")
            return True

    def _checkout_with_fresh_strategy(self, target: str, target_type: str) -> bool:
        """Fresh 전략으로 체크아웃 수행"""
        print("🗑️  Using fresh strategy (remove → clone → checkout)...")

        # 1. Remove existing directory
        if not self.git_manager.remove_directory():
            return False

        # 2. Clone fresh
        if not self.git_manager.clone_repository():
            return False

        # 3. Checkout specific target
        if not self._perform_checkout(target, target_type):
            return False

        print("✅ Fresh strategy checkout completed!")
        return True

    def checkout_with_strategy(
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
        emoji = self._get_checkout_emoji(target_type)
        print(f"🚀 Starting {target_type} checkout: {target}")

        # Strategy 검증
        if strategy not in ["fresh", "preserve"]:
            print(f"❌ Invalid strategy: {strategy}. Use 'fresh' or 'preserve'")
            return False

        # 전략에 따라 체크아웃 수행
        if strategy == "preserve":
            return self._checkout_with_preserve_strategy(target, target_type)
        else:
            return self._checkout_with_fresh_strategy(target, target_type)

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
        return self.checkout_with_strategy(branch_name, "branch", strategy)

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
        if not self.git_manager._is_git_repo() and strategy == "preserve":
            print(f"❌ Not a Git repository: {self.git_manager.local_path}")
            return False

        return self.checkout_with_strategy(commit_hash, "commit", strategy)

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
        if not self.git_manager._is_git_repo() and strategy == "preserve":
            print(f"❌ Not a Git repository: {self.git_manager.local_path}")
            return False

        return self.checkout_with_strategy(tag_name, "tag", strategy)
