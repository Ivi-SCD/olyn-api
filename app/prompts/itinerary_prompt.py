from datetime import date, timedelta


def build_itinerary_prompt(
    num_days: int,
    start_time: str,
    end_time: str,
    start_date: date,
    companion_type: str,
    interests: dict[str, float],
    budget: str,
) -> str:
    top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
    interest_lines = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v:.1f}" for k, v in top_interests
    )

    days_info = []
    for i in range(num_days):
        d = start_date + timedelta(days=i)
        weekday = d.strftime("%A")
        days_info.append(f"  - Day {i + 1}: {d.isoformat()} ({weekday})")
    days_text = "\n".join(days_info)

    return f"""Generate a detailed {num_days}-day travel itinerary for Olinda, Pernambuco, Brazil.

TRAVELER PROFILE:
- Companion type: {companion_type}
- Budget level: {budget}
- Available daily: {start_time} to {end_time}
- Interest scores (0.0 to 1.0, higher = more interested):
{interest_lines}

DATES:
{days_text}

RULES:
1. Schedule activities ONLY between {start_time} and {end_time} each day.
2. Prioritize attractions matching the highest interest scores.
3. Respect budget level: ECONOMY (free/cheap activities), STANDARD (mid-range), LUXURY (premium experiences).
4. Include realistic travel time between stops (Olinda is walkable, 5-15min between most attractions).
5. Never repeat the same place across different days.
6. Include a mix of well-known landmarks and hidden local gems.
7. For FAMILY companions, prefer family-friendly activities. For COUPLE, include romantic spots. For FRIENDS, include social/nightlife options. For SOLO, include cultural immersion.
8. Include estimated cost in BRL for each activity (0 if free).

RESPOND WITH VALID JSON ONLY in this exact structure:
{{
  "title": "X Days in Olinda",
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "weekday": "DayName",
      "items": [
        {{
          "start_time": "HH:MM",
          "end_time": "HH:MM",
          "place_name": "Exact place name as it appears on Google Maps",
          "description": "2-3 sentence description of the activity",
          "historical_context": "1-2 sentences about the history or cultural significance",
          "estimated_cost": 0.0,
          "travel_mode": "WALKING"
        }}
      ]
    }}
  ]
}}"""
