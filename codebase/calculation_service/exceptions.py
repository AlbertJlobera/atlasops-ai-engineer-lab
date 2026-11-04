class CalculationTimeoutError(Exception):
    """Raised when a calculation exceeds the configured processing timeout."""

    def __init__(self, calculation_id: str, timeout_seconds: int):
        self.calculation_id = calculation_id
        self.timeout_seconds = timeout_seconds

        super().__init__(
            f"Calculation {calculation_id} exceeded "
            f"{timeout_seconds} seconds."
        )