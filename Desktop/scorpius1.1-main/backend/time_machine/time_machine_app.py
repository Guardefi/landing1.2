"""
Time Machine Application Entry Point
Provides unified CLI and server startup for the Time Machine platform
"""

import asyncio
import os
import sys
from pathlib import Path

import click

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging_config import configure_for_environment

# from packages.core.cli.tm import tm as tm_cli
# from packages.core.core.controller import TimeMachineEngine


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
def main(debug, config):
    """Time Machine - Blockchain Forensic Analysis Platform"""
    # Configure logging
    env = "development" if debug else "production"
    configure_for_environment(env)


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host, port, reload):
    """Start the Time Machine API server"""
    import uvicorn

    # Configure the app
    app_str = "time_machine.api.app:app"

    click.echo(f"Starting Time Machine server on {host}:{port}")
    click.echo("API Documentation available at: http://localhost:8000/docs")

    uvicorn.run(app_str, host=host, port=port, reload=reload, log_level="info")


# @main.command()
# @click.pass_context
# def cli(ctx):
#     """Run Time Machine CLI commands"""
#     # Import and run the CLI
#     ctx.invoke(tm_cli)


@main.command()
def init():
    """Initialize Time Machine workspace"""
    click.echo("Initializing Time Machine workspace...")

    # Create directories
    dirs = ["store/snapshots", "store/bundles", "logs", "config"]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        click.echo(f"Created directory: {dir_path}")

    # Create default config
    config_path = Path("config/time_machine.yaml")
    if not config_path.exists():
        default_config = """# Time Machine Configuration
engine:
  max_concurrent_jobs: 5
  snapshot_retention_days: 30
  cleanup_interval_hours: 24

vm_adapters:
  anvil:
    enabled: true
    default_port: 8545
    default_chain_id: 31337
    fork_url: null
  
  hardhat:
    enabled: true
    default_port: 8545
    
  geth:
    enabled: false

storage:
  snapshots_dir: "store/snapshots"
  bundles_dir: "store/bundles"
  compression: true
  deduplication: true

logging:
  level: INFO
  file: "logs/time_machine.log"
  json_format: true

plugins:
  gas_analysis:
    enabled: true
  anvil_adapter:
    enabled: true
"""
        config_path.write_text(default_config)
        click.echo(f"Created config file: {config_path}")

    click.echo("✓ Time Machine workspace initialized successfully!")


# @main.command()
# def test():
#     """Run basic system tests"""
#     click.echo("Running Time Machine system tests...")
# 
#     async def run_tests():
#         try:
#             # Initialize engine
#             engine = TimeMachineEngine()
#             await engine.initialize()
# 
#             # Test basic functionality
#             click.echo("✓ Engine initialization")
# 
#             # Test VM adapter registry
#             from packages.core.core.models import VMType
# 
#             assert VMType.ANVIL in engine.vm_adapters
#             click.echo("✓ VM adapter registry")
# 
#             # Cleanup
#             await engine.cleanup()
#             click.echo("✓ Engine cleanup")
# 
#             click.echo("✅ All tests passed!")
#             return 0
#         except Exception as e:
#             click.echo(f"❌ Test failed: {e}", err=True)
#             return 1
# 
#     return asyncio.run(run_tests())


# @main.command()
# def demo():
#     """Run a demonstration of Time Machine functionality"""
#     click.echo("🚀 Time Machine Demo")
#     click.echo("=" * 50)
# 
#     async def run_demo():
#         try:
#             # Initialize
#             engine = TimeMachineEngine()
#             await engine.initialize()
#             click.echo("✓ Initialized Time Machine engine")
# 
#             # Create a demo replay job
#             from packages.core.core.models import VMType
# 
#             job = await engine.create_replay_job(
#                 start_block=100,
#                 end_block=105,
#                 vm_type=VMType.ANVIL,
#                 config={"demo": True},
#             )
#             click.echo(f"✓ Created demo replay job: {job.id}")
# 
#             # List jobs
#             jobs = await engine.list_jobs()
#             click.echo(f"✓ Total jobs in system: {len(jobs)}")
# 
#             # Get engine stats
#             stats = await engine.get_engine_stats()
#             click.echo(f"✓ Engine stats: {stats}")
# 
#             click.echo("🎉 Demo completed successfully!")
# 
#             await engine.cleanup()
#         except Exception as e:
#             click.echo(f"❌ Demo failed: {e}", err=True)
#             return 1
# 
#     return asyncio.run(run_demo())


@main.command()
def version():
    """Show Time Machine version information"""
    click.echo("Time Machine v1.0.0")
    click.echo("Enterprise Blockchain Forensic Analysis Platform")
    click.echo("Built with ❤️  for security researchers and analysts")


if __name__ == "__main__":
    main()
