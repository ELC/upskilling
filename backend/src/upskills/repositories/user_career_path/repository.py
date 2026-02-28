from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import Career as CareerDomain
from upskills.domain import PathTemplate as PathTemplateDomain
from upskills.domain import UserCareerPath as UserCareerPathDomain
from upskills.domain import UserPathAssignment as UserPathAssignmentDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user_path_assignment.models import UserPathAssignment

from .mapper import UserCareerPathMapper
from .models import UserCareerPath


class UserCareerPathRepository(BaseRepository[UserCareerPath, UserCareerPathDomain, UserCareerPathMapper]):
    _id_column = "user_career_path_id"

    async def get_by_id(self, id_value: int) -> UserCareerPath | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                )
                .where(UserCareerPath.user_career_path_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[UserCareerPathDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments),
                )
                .where(UserCareerPath.user_id == user_id)
            )
            result = await session.execute(stmt)
            return [self.to_domain(p, include_assignments=True) for p in result.scalars().all()]

    async def get_active_for_user(self, user_id: int) -> UserCareerPath | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                )
                .where(UserCareerPath.user_id == user_id)
                .order_by(UserCareerPath.start_date.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    def to_domain(path: UserCareerPath, *, include_assignments: bool = False) -> UserCareerPathDomain:
        career = CareerDomain.model_validate(path.career) if path.career else None

        path_assignments = []
        if include_assignments and path.path_assignments:
            path_assignments = [
                UserPathAssignmentDomain(
                    user_path_assignment_id=a.user_path_assignment_id,
                    path_template=PathTemplateDomain.model_validate(a.path_template) if a.path_template else None,
                    start_date=a.start_date,
                    deadline=a.deadline,
                    status=a.status,
                    progress_percent=a.progress_percent,
                    mentor_validation_status=a.mentor_validation_status,
                )
                for a in path.path_assignments
            ]

        return UserCareerPathDomain(
            user_career_path_id=path.user_career_path_id,
            career=career,
            start_date=path.start_date,
            end_date=path.end_date,
            overall_progress_percent=path.overall_progress_percent,
            career_name=path.career.name if path.career else None,
            career_specialization=path.career.specialization if path.career else None,
            path_assignments=path_assignments,
        )
