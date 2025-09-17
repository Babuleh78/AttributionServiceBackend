def calc(item):
    stats = {
        stat["IntervalGroup"]: {
            "Frequency": stat["Frequency"],
            "StdDev": stat["StdDev"]
        }
        for stat in item.get("interval_stats", [])
    }

    seconds = stats.get("Унисоны и секунды", {"Frequency": 0, "StdDev": 0})
    thirds = stats.get("Терции", {"Frequency": 0, "StdDev": 0})
    octaves = stats.get("Октавы", {"Frequency": 0, "StdDev": 0})

    return (
        item["price"] *
        item["length"] 
        // 60 
        * 0.8
        + 10*(
            thirds["Frequency"] * thirds["StdDev"] * 0.3
            + seconds["Frequency"] * seconds["StdDev"] * 0.4
            + octaves["Frequency"] * octaves["StdDev"] * 0.6
        ) 
    )