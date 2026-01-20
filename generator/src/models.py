from dataclasses import dataclass
from typing import Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class GeneticConfigModel(BaseModel):
    population_size: Optional[int] = Field(300, ge=50, le=1000, description="Размер популяции")
    generations: Optional[int] = Field(300, ge=50, le=1000, description="Количество поколений")
    elitism_rate: Optional[float] = Field(0.2, ge=0.1, le=0.5, description="Доля элитных особей")
    survival_rate: Optional[float] = Field(0.8, ge=0.5, le=0.95, description="Доля выживающих особей")

@dataclass
class GeneticConfig:
    population_size: int = 300
    generations: int = 300
    elitism_rate: float = 0.2
    survival_rate: float = 0.8
    
    def to_model(self) -> GeneticConfigModel:
        return GeneticConfigModel(
            population_size=self.population_size,
            generations=self.generations,
            elitism_rate=self.elitism_rate,
            survival_rate=self.survival_rate
        )
    
    @classmethod
    def from_model(cls, model: GeneticConfigModel) -> 'GeneticConfig':
        return cls(
            population_size=model.population_size or 300,
            generations=model.generations or 300,
            elitism_rate=model.elitism_rate or 0.2,
            survival_rate=model.survival_rate or 0.8
        )

@dataclass
class Lesson:
    lecturer: str
    subject: str
    time_slot: str


@dataclass
class DaySchedule:
    day: str
    lessons: List[Lesson]


@dataclass
class GroupSchedule:
    group: str
    days: List[DaySchedule]


@dataclass
class ScheduleMetadata:
    generated_at: str
    groups: List[str]
    subjects: List[str]
    teachers: List[str]
    lesson_slots: List[str]
    days_of_week: List[str]
    locked_slots: List[Any]


@dataclass
class ScheduleModel:
    metadata: ScheduleMetadata
    schedule: Dict[str, Dict[str, List[Lesson]]]  # {group: {day: [Lesson]}}


@dataclass
class APIMessageModel:
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class APIResponseModel(APIMessageModel):
    schedule: Optional[ScheduleModel] = None