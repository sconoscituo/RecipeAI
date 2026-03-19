from enum import Enum
class PlanType(str, Enum):
    FREE = "free"; PRO = "pro"  # 월 4,900원
PLAN_LIMITS = {
    PlanType.FREE: {"scans_per_day": 3, "saved_recipes": 10, "shopping_list": False},
    PlanType.PRO:  {"scans_per_day": 30,"saved_recipes": 999,"shopping_list": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 4900}
