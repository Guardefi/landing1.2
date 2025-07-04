# Example call after opportunity found:
# log_arbitrage_opportunity("DAI/WETH", 47, 0.8)


def log_arbitrage_opportunity(pair: str, profit: float, confidence: float) -> None:
    """Log an arbitrage opportunity for demo purposes."""
    print(
        f"Arbitrage opportunity found: {pair}, "
        f"profit: {profit}, confidence: {confidence}"
    )


# Example usage:
log_arbitrage_opportunity("DAI/WETH", 47, 0.8)
