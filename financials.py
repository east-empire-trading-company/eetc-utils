def compound_interest(amount: float, period: int, interest: float) -> float:
    """
    Calculates compound interest
    """

    for x in range(0, period):
        amount = amount + amount * (interest / 100)

    return round(amount, 2)
