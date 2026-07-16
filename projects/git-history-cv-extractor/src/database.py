from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine, func, select


class Config(SQLModel, table=True):
    __tablename__: str = "config"
    key: str = Field(primary_key=True)
    value: str


class Repository(SQLModel, table=True):
    __tablename__: str = "repositories"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    url: str
    local_path: str
    last_scanned_commit: str | None = None
    last_scanned_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Commit(SQLModel, table=True):
    __tablename__: str = "commits"
    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repositories.id")
    hash: str = Field(unique=True, index=True)
    author_name: str
    author_email: str
    commit_date: str  # ISO 8601 string: YYYY-MM-DD HH:MM:SS
    message: str


class FileChange(SQLModel, table=True):
    __tablename__: str = "file_changes"
    id: int | None = Field(default=None, primary_key=True)
    commit_id: int = Field(foreign_key="commits.id")
    file_path: str
    file_extension: str
    additions: int
    deletions: int


class RepositoryStore:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def get_config(self, key: str) -> str | None:
        with Session(self.engine) as session:
            statement = select(Config).where(Config.key == key)
            config = session.exec(statement).first()
            return config.value if config else None

    def set_config(self, key: str, value: str):
        with Session(self.engine) as session:
            statement = select(Config).where(Config.key == key)
            config = session.exec(statement).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value)
            session.add(config)
            session.commit()

    def add_repository(self, name: str, url: str, local_path: str) -> int:
        with Session(self.engine) as session:
            statement = select(Repository).where(Repository.name == name)
            repo = session.exec(statement).first()
            if repo:
                return repo.id  # type: ignore

            repo = Repository(name=name, url=url, local_path=local_path)
            session.add(repo)
            session.commit()
            session.refresh(repo)
            return repo.id  # type: ignore

    def update_repository_scanned(self, repo_id: int, commit_hash: str):
        with Session(self.engine) as session:
            repo = session.get(Repository, repo_id)
            if repo:
                repo.last_scanned_commit = commit_hash
                repo.last_scanned_at = datetime.now(timezone.utc)
                session.add(repo)
                session.commit()

    def add_commit(
        self,
        repo_id: int,
        commit_hash: str,
        author_name: str,
        author_email: str,
        commit_date: str,
        message: str,
    ) -> int:
        with Session(self.engine) as session:
            statement = select(Commit).where(Commit.hash == commit_hash)
            existing = session.exec(statement).first()
            if existing:
                return existing.id  # type: ignore

            new_commit = Commit(
                repo_id=repo_id,
                hash=commit_hash,
                author_name=author_name,
                author_email=author_email,
                commit_date=commit_date,
                message=message,
            )
            session.add(new_commit)
            session.commit()
            session.refresh(new_commit)
            return new_commit.id  # type: ignore

    def add_file_change(
        self, commit_id: int, file_path: str, additions: int, deletions: int
    ):
        with Session(self.engine) as session:
            # Resolve extension in lowercase
            extension = Path(file_path).suffix.lower()
            if not extension:
                extension = "no-ext"

            change = FileChange(
                commit_id=commit_id,
                file_path=file_path,
                file_extension=extension,
                additions=additions,
                deletions=deletions,
            )
            session.add(change)
            session.commit()

    def get_repo_stats(self, repo_id: int) -> dict:
        with Session(self.engine) as session:
            # Total commits
            commits_statement = select(func.count(1)).where(Commit.repo_id == repo_id)
            total_commits = session.exec(commits_statement).first() or 0

            # Get all commit IDs for this repo
            commit_ids_statement = select(Commit.id).where(Commit.repo_id == repo_id)
            commit_ids = session.exec(commit_ids_statement).all()

            if not commit_ids:
                return {
                    "total_commits": 0,
                    "files_changed": 0,
                    "total_additions": 0,
                    "total_deletions": 0,
                }

            # Files changed (distinct paths)
            distinct_paths = func.distinct(FileChange.file_path)
            files_statement = select(func.count(distinct_paths)).where(
                FileChange.commit_id.in_(commit_ids)  # type: ignore
            )
            files_changed = session.exec(files_statement).first() or 0

            # Total additions & deletions
            additions_statement = select(func.sum(FileChange.additions)).where(
                FileChange.commit_id.in_(commit_ids)  # type: ignore
            )
            total_additions = session.exec(additions_statement).first() or 0

            deletions_statement = select(func.sum(FileChange.deletions)).where(
                FileChange.commit_id.in_(commit_ids)  # type: ignore
            )
            total_deletions = session.exec(deletions_statement).first() or 0

            return {
                "total_commits": total_commits,
                "files_changed": files_changed,
                "total_additions": int(total_additions),
                "total_deletions": int(total_deletions),
            }

    def get_all_repositories(self) -> list[Repository]:
        with Session(self.engine) as session:
            return list(session.exec(select(Repository)).all())

    def get_repository_commits(self, repo_id: int) -> list[Commit]:
        with Session(self.engine) as session:
            return list(
                session.exec(
                    select(Commit)
                    .where(Commit.repo_id == repo_id)
                    .order_by(Commit.commit_date)
                ).all()
            )

    def get_commits_file_changes(self, commit_ids: list[int]) -> list[FileChange]:
        if not commit_ids:
            return []
        with Session(self.engine) as session:
            return list(
                session.exec(
                    select(FileChange).where(FileChange.commit_id.in_(commit_ids))  # type: ignore
                ).all()
            )

    def get_repository_count(self) -> int:
        with Session(self.engine) as session:
            return len(session.exec(select(Repository)).all())

    def get_repository(self, repo_id: int) -> Repository | None:
        with Session(self.engine) as session:
            return session.get(Repository, repo_id)
