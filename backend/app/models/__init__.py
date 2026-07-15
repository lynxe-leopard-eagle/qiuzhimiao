"""模型包初始化。"""

from app.core.database import Base  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.growth import GrowthRecord  # noqa: F401
from app.models.interview import Evaluation, Interview, Message, Review  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.user import User  # noqa: F401
