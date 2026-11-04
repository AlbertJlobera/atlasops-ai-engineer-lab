import asyncio

from calculation_service.config import (
    CALCULATION_TIMEOUT_SECONDS,
)
from calculation_service.exceptions import (
    CalculationTimeoutError,
)


async def run_calculation(
    calculation_id: str,
    calculation_type: str,
    payload: dict,
) -> dict:
    try:
        return await asyncio.wait_for(
            _execute_calculation(
                calculation_type=calculation_type,
                payload=payload,
            ),
            timeout=CALCULATION_TIMEOUT_SECONDS,
        )

    except asyncio.TimeoutError as exc:
        raise CalculationTimeoutError(
            calculation_id=calculation_id,
            timeout_seconds=CALCULATION_TIMEOUT_SECONDS,
        ) from exc


async def _execute_calculation(
    calculation_type: str,
    payload: dict,
) -> dict:

    # Simplified AtlasOps calculation engine.
    await asyncio.sleep(0.1)

    return {
        "calculation_type": calculation_type,
        "status": "completed",
        "result": payload,
    }