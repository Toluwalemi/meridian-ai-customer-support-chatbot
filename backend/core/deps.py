from dataclasses import dataclass
from typing import Annotated, Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.logging import logger
from core.settings import settings


@dataclass(frozen=True)
class AuthenticatedUser:
    sub: str
    email: str | None
    raw_claims: dict[str, Any]


class ClerkJwtVerifier:
    """Verifies Clerk-issued JWTs against the published JWKS."""

    def __init__(self, jwks_url: str, issuer: str, audience: str | None) -> None:
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience or None
        self._jwks: dict[str, Any] | None = None

    async def _load_jwks(self) -> dict[str, Any]:
        if self._jwks is not None:
            return self._jwks
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(self.jwks_url)
            resp.raise_for_status()
            self._jwks = resp.json()
        return self._jwks

    async def verify(self, token: str) -> AuthenticatedUser:
        try:
            jwks = await self._load_jwks()
            unverified = jwt.get_unverified_header(token)
            kid = unverified.get("kid")
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if key is None:
                self._jwks = None
                jwks = await self._load_jwks()
                key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if key is None:
                raise JWTError("Signing key not found")

            options = {"verify_aud": bool(self.audience)}
            claims = jwt.decode(
                token,
                key,
                algorithms=[key.get("alg", "RS256")],
                issuer=self.issuer,
                audience=self.audience,
                options=options,
            )
        except (JWTError, httpx.HTTPError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        return AuthenticatedUser(
            sub=str(claims["sub"]),
            email=claims.get("email") or claims.get("primary_email_address"),
            raw_claims=claims,
        )


_verifier = ClerkJwtVerifier(
    jwks_url=str(settings.clerk_jwks_url),
    issuer=str(settings.clerk_issuer).rstrip("/"),
    audience=settings.clerk_audience,
)

_dev_bypass_active = settings.env == "dev" and settings.auth_dev_bypass
_bearer = HTTPBearer(auto_error=not _dev_bypass_active)

if _dev_bypass_active:
    logger.warning("auth.dev_bypass_enabled", env=settings.env)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> AuthenticatedUser:
    if _dev_bypass_active and credentials is None:
        return AuthenticatedUser(sub="dev-user", email="dev@local", raw_claims={})
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _verifier.verify(credentials.credentials)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
