"""데이터 모델

FAQ, State, Ticket 데이터 모델을 정의하는 모듈입니다.
"""

from .faq import FAQDocument, FAQContent, FAQSolution
from .state import SupportState, SolutionStep
from .ticket import Ticket

__all__ = [
    "FAQDocument",
    "FAQContent",
    "FAQSolution",
    "SupportState",
    "SolutionStep",
    "Ticket",
]
