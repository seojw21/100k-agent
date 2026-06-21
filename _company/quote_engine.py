from pydantic import BaseModel, Field
from typing import List


class FilmPackage(BaseModel):
    difficulty_level: int = Field(..., ge=1, le=3)  # 난이도 1~3단계
    labor_count: int = Field(..., gt=0)             # 작업 인원 수
    film_volume: float = Field(..., gt=0.0)         # m² 또는 롤 단위 가변비용 대상
    submaterial_cost: float = Field(default=0.0, ge=0.0)  # 부자재 비용

def calculate_package_price(difficulty: int, labor_count: int, film_volume: float, submaterial_cost: float) -> float:
    """
    확정된 견적 수식 C = Ps + (W × B) 구현.
    Ps: 난이도별 고정 단가 (49/79/129만원 기준), W: 작업 인원수, B: 가변비 합계(film_volume * unit_cost).
    """
    # 부산·울산·경남 지역 3단계 고정 단가 적용 (단위: 만원)
    fixed_prices = {1: 49, 2: 79, 3: 129}
    ps = fixed_prices.get(difficulty, 49)

    # 가변비 계산 - film_volume에 대한 단위 단가는 비즈니스 정책을 따름 (예시로 0.5 적용 가능하나 여기선 구조 위주 구현)
    variable_unit_cost = 0.5  # 실제 운영 시 config에서 로드하도록 설계
    w = labor_count
    b = film_volume * variable_unit_cost

    return ps + (w * b) + submaterial_cost