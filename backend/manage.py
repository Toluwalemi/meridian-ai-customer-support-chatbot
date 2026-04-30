import asyncio

import typer
import uvicorn

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def runserver(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    uvicorn.run("main:app", host=host, port=port, reload=reload)


@cli.command()
def probe_mcp() -> None:
    """List the MCP server's tools and exit."""
    from apps.mcp.services import mcp_service

    async def _run() -> None:
        await mcp_service.connect()
        for tool in mcp_service.tools:
            typer.echo(f"- {tool['name']}: {tool['description'][:80]}")
        await mcp_service.close()

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
