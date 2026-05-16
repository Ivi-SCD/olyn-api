from enum import StrEnum


class CompanionType(StrEnum):
    SOLO = "SOLO"
    COUPLE = "COUPLE"
    FAMILY = "FAMILY"
    FRIENDS = "FRIENDS"


class BudgetLevel(StrEnum):
    ECONOMY = "ECONOMY"
    STANDARD = "STANDARD"
    LUXURY = "LUXURY"


class TravelMode(StrEnum):
    DRIVING = "DRIVING"
    WALKING = "WALKING"
    TRANSIT = "TRANSIT"
