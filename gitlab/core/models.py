from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import functions


class Base(DeclarativeBase):
    pass


class PollEntry(Base):
    '''Represents an entry of a GitLab instance poll.'''
    __tablename__ = 'poll_entry'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    base_url: Mapped[datetime] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=functions.now(), nullable=True, index=True)
    health_check_passed: Mapped[bool] = mapped_column(Boolean, index=True)
    instance_version: Mapped[str] = mapped_column(String, index=True)
    readiness_check_passed: Mapped[bool] = mapped_column(Boolean, index=True)
    # extra information from the calls made
    health_check_response: Mapped[str] = mapped_column(
        String,
        default='',
        deferred=True,
        deferred_group='response_bodies',
    )
    readiness_check_response: Mapped[str] = mapped_column(
        String,
        default='',
        deferred=True,
        deferred_group='response_bodies',
    )
    metadata_response: Mapped[str] = mapped_column(
        String,
        default='',
        deferred=True,
        deferred_group='response_bodies',
    )
    # error-related information
    error_message: Mapped[str] = mapped_column(String, default='')

    def __repr__(self) -> 'str':
        return f'<{self.__class__.__name__} ({{attributes}})>'.format(
            attributes=', '.join((
                f'instance={self.base_url}',
                f'health={"passed" if self.health_check_passed else "failed"}',
                f'readiness={"passed" if self.readiness_check_passed else "failed"}',
                f'version={self.instance_version}',
                f'timestamp={self.created_at.isoformat()}',
            ))
        )
