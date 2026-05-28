def should_reject_short_stay(stay_days, min_nights, allow_short_stay=False):
    return stay_days < min_nights and not allow_short_stay
