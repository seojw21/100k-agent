from pydantic import BaseModel, Field
from typing import List
import os
import json


class FilmPackage(BaseModel):
    difficulty_level: int = Field(..., ge=1, le=3)  # 난이도 1~3단계
    labor_count: int = Field(..., gt=0)             # 작업 인원 수
    film_volume: float = Field(..., gt=0.0)         # m² 또는 롤 단위 가변비용 대상 (미터 단위)
    submaterial_cost: float = Field(default=0.0, ge=0.0)  # 부자재 비용
    brand: str = Field(default="한솔")               # 대리점 브랜드 (한솔, 삼성, 현대, LX, 영림, 예림)
    product_type: str = Field(default="단색(솔리드)")  # 품명 또는 제품 코드 분류
    margin_per_meter: float = Field(default=1200.0, ge=1000.0, le=1500.0) # 1m당 플러스 마진 (1000원 ~ 1500원)
    is_fire_resistant: bool = Field(default=False)    # 방염 여부 (예림 브랜드 등 가산 비용 처리용)


def get_base_price(brand: str, product_type: str) -> float:
    """
    film_prices.json 파일로부터 특정 브랜드 및 제품군의 시공가(원가)를 로드합니다.
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "film_prices.json")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"인테리어필름 가격표 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if brand not in data:
        raise ValueError(f"존재하지 않는 대리점 브랜드입니다: {brand}. (한솔, 삼성, 현대, LX, 영림, 예림 중 입력)")
        
    brand_data = data[brand]
    prices = brand_data["prices"]
    
    # 1. 완전 일치 여부 확인
    if product_type in prices:
        return float(prices[product_type])
        
    # 2. 부분 일치 확인 (대소문자 무관 및 공백 제거 비교)
    norm_product_type = product_type.replace(" ", "").lower()
    for key, val in prices.items():
        norm_key = key.replace(" ", "").lower()
        if norm_product_type in norm_key or norm_key in norm_product_type:
            return float(val)
            
    # 매칭되는 제품군이 없을 경우 예외 발생
    available_keys = ", ".join(prices.keys())
    raise ValueError(f"브랜드 '{brand}'에서 제품군 '{product_type}'을(를) 찾을 수 없습니다. 선택 가능 제품군: {available_keys}")


def calculate_package_price(
    difficulty: int,
    labor_count: int,
    film_volume: float,
    submaterial_cost: float,
    brand: str = "한솔",
    product_type: str = "단색(솔리드)",
    margin_per_meter: float = 1200.0,
    is_fire_resistant: bool = False
) -> float:
    """
    확정된 견적 수식 C = Ps + (W × B) + submaterial_cost 구현.
    Ps: 난이도별 고정 단가 (49/79/129만원 기준 -> 원화 단위 변환)
    W: 작업 인원수
    B: 가변비 합계 (film_volume * 최종 단가)
    최종 단가: 대리점 시공 원가 + 1m당 플러스 마진(1,000원 ~ 1,500원)
              (단, 예림 브랜드의 방염 요청 시 원가에 +4,400원 가산)
    """
    # 1. 부산·울산·경남 지역 3단계 고정 단가 적용 (단위: 만원 -> 원화 환산)
    fixed_prices = {1: 49, 2: 79, 3: 129}
    ps_manwon = fixed_prices.get(difficulty, 49)
    ps_krw = ps_manwon * 10000.0

    # 2. 대리점 가격표에서 시공 원가 가져오기
    base_cost = get_base_price(brand, product_type)

    # 2.1. 예림 브랜드이고 방염인 경우 시공자 단가 4,400원 가산 적용
    if brand == "예림":
        if is_fire_resistant or "방염" in product_type:
            base_cost += 4400.0

    # 3. 가변 단가 = 원가 + 마진(1,000 ~ 1,500원)
    # margin_per_meter 값 범위 제한 보장
    actual_margin = max(1000.0, min(1500.0, margin_per_meter))
    variable_unit_cost = base_cost + actual_margin

    # 4. 가변비 합계 B = film_volume * variable_unit_cost
    b = film_volume * variable_unit_cost
    w = labor_count

    # 최종 금액 = 고정비 + (인원수 * 가변비) + 부자재 비용
    total_price = ps_krw + (w * b) + submaterial_cost
    return total_price