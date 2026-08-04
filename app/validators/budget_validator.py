def validate_budget(total_budget, budget):

    spent = (
        budget["hotel"]
        + budget["food"]
        + budget["transport"]
        + budget["activities"]
    )

    if spent <= total_budget:
        budget["remaining"] = total_budget -spent
        return budget

    scale = total_budget / spent

    budget["hotel"] = int(budget["hotel"] * scale)
    budget["food"] = int(budget["food"] * scale)
    budget["transport"] = int(budget["food"] * scale)
    budget["activities"] = int(budget["activities"] * scale)

    spent = (
            budget["hotel"]
            + budget["food"]
            + budget["transport"]
            + budget["activities"]
        )

    budget["remaining"] = total_budget - spent

    return budget