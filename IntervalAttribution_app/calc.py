def calc(composer_interval_stats, anonymous_interval_stats):

    if not composer_interval_stats or not anonymous_interval_stats:
        return 0.0

    comp_dict = {item["IntervalGroup"]: item["Frequency"] for item in composer_interval_stats}
    anon_dict = {item["IntervalGroup"]: item["Frequency"] for item in anonymous_interval_stats}

    common_groups = set(comp_dict.keys()) & set(anon_dict.keys())
    if not common_groups:
        return 0.0

    total_diff = sum(abs(comp_dict[group] - anon_dict[group]) for group in common_groups)
    avg_diff = total_diff / len(common_groups)
    match_percent = max(0.0, 100.0 - avg_diff)
    return round(match_percent, 1)