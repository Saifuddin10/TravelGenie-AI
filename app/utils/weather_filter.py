def filter_places_by_weather(places, weather):

    condition = weather.get("condition", "").lower()
    description = weather.get("description", "").lower()

    rain_conditions = [
        "rain",
        "drizzle",
        "thunderstorm"
    ]

    is_raining = any(
        word in condition or word in description
        for word in rain_conditions
    )

    if is_raining:

        indoor_places = [
            place
            for place in places
            if place.get("type", "").lower() == "indoor"
        ]

        print("\nWeather Filter:")
        print("Rain detected.")
        print(f"Indoor attractions available: {len(indoor_places)}")

        return indoor_places

    print("\nWeather Filter:")
    print("No rain detected. Using all attractions.")

    return places