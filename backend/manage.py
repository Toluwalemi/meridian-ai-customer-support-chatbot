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


@cli.command()
def chat() -> None:
    """Interactive REPL against the live MCP + LLM. No HTTP, no auth."""
    from apps.chat.schemas import ChatMessage
    from apps.chat.services import ChatService
    from apps.mcp.services import mcp_service

    async def _run() -> None:
        await mcp_service.connect()
        service = ChatService(mcp_service)
        history: list[ChatMessage] = []
        typer.echo(
            "Meridian chat REPL. Type 'quit' to exit, '/reset' to clear history."
        )
        try:
            while True:
                try:
                    user_text = typer.prompt("you", prompt_suffix="> ")
                except (EOFError, KeyboardInterrupt):
                    break
                stripped = user_text.strip()
                if stripped.lower() in {"quit", "exit"}:
                    break
                if stripped == "/reset":
                    history.clear()
                    typer.echo("(history cleared)")
                    continue
                history.append(ChatMessage(role="user", content=user_text))
                response = await service.reply(history)
                history.append(ChatMessage(role="assistant", content=response.reply))
                for trace in response.tool_calls:
                    typer.echo(
                        f"  [tool] {trace.name} args={trace.arguments}"
                    )
                typer.echo(f"bot> {response.reply}\n")
        finally:
            await mcp_service.close()

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
