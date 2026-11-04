from calculation_service.config import (
    CALCULATION_TIMEOUT_ERROR_CODE,
)
from calculation_service.exceptions import (
    CalculationTimeoutError,
)
from calculation_service.processor import (
    run_calculation,
)


async def calculate(request: dict) -> dict:
    try:
        result = await run_calculation(
            calculation_id=request["calculation_id"],
            calculation_type=request["calculation_type"],
            payload=request["payload"],
        )

        return {
            "status": "success",
            "data": result,
        }

    except CalculationTimeoutError as exc:
        return {
            "status": "error",
            "error_code": CALCULATION_TIMEOUT_ERROR_CODE,
            "message": (
                f"Calculation exceeded the processing timeout "
                f"of {exc.timeout_seconds} seconds."
            ),
            "calculation_id": exc.calculation_id,
        }