import httpx
from fastapi import HTTPException, status


async def forward_json(
    *,
    method: str,
    url: str,
    body: dict[str, object] | None = None,
    downstream_name: str,
    default_error: str,
) -> dict[str, object]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method=method, url=url, json=body)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach {downstream_name}",
        ) from exc

    if response.status_code >= 500:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{downstream_name} returned an unexpected error",
        )

    if response.status_code >= 400:
        detail = default_error
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()
