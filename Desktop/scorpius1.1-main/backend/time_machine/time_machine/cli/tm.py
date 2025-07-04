"""
Time Machine CLI Interface
Command-line interface for blockchain forensic analysis operations.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from ..core.controller import TimeMachineEngine
from ..core.models import JobStatus, ReplayJob, SessionType, VMBackend

console = Console()

# Global engine instance
engine = None


async def get_engine():
    """Get or create engine instance."""
    global engine
    if engine is None:
        engine = TimeMachineEngine()
        await engine.start()
    return engine


def run_async(coro):
    """Run async function in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", help="Configuration file path")
def tm(verbose, config):
    """
    Time Machine CLI for blockchain forensic analysis.

    Advanced blockchain state replay, patching, and forensic analysis tools.
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")

    if config:
        console.print(f"[dim]Using config file: {config}[/dim]")


@tm.command()
@click.option("--tx", help="Transaction hash to replay")
@click.option("--block", type=int, help="Block number to replay")
@click.option("--from-block", type=int, help="Start block for range replay")
@click.option("--to-block", type=int, help="End block for range replay")
@click.option(
    "--vm",
    default="anvil",
    type=click.Choice(["anvil", "hardhat", "geth"]),
    help="VM backend to use",
)
@click.option("--name", help="Human-readable name for the replay")
@click.option("--description", help="Description of the replay purpose")
@click.option("--fork-url", help="Blockchain RPC URL to fork from")
@click.option("--output", "-o", help="Output file for results")
@click.option("--patches", help="JSON file with patches to apply")
@click.option("--watch", is_flag=True, help="Watch replay progress in real-time")
def replay(
    tx,
    block,
    from_block,
    to_block,
    vm,
    name,
    description,
    fork_url,
    output,
    patches,
    watch,
):
    """
    Replay blockchain transactions or blocks.

    Examples:
        tm replay --tx 0x123... --vm anvil
        tm replay --block 12345 --name "Block Analysis"
        tm replay --from-block 100 --to-block 200 --patches patches.json
    """

    async def _replay():
        engine = await get_engine()

        # Load patches if provided
        patch_list = []
        if patches:
            try:
                with open(patches, "r") as f:
                    patch_list = json.load(f)
                console.print(
                    f"[green]Loaded {len(patch_list)} patches from {patches}[/green]"
                )
            except Exception as e:
                console.print(f"[red]Failed to load patches: {e}[/red]")
                return

        # Create replay job
        job = ReplayJob(
            name=name or f"CLI-Replay-{int(datetime.now().timestamp())}",
            description=description or "",
            tx_hash=tx,
            block_number=block,
            from_block=from_block,
            to_block=to_block,
            vm_backend=VMBackend(vm),
            patches=patch_list,
            metadata={"fork_url": fork_url} if fork_url else {},
        )

        # Show job info
        with Panel(
            f"[bold]Replay Job[/bold]\n"
            f"ID: {job.job_id}\n"
            f"Name: {job.name}\n"
            f"VM: {vm}\n"
            f"TX: {tx or 'N/A'}\n"
            f"Block: {block or 'N/A'}\n"
            f"Range: {from_block or 'N/A'} - {to_block or 'N/A'}\n"
            f"Patches: {len(patch_list)}",
            title="Starting Replay",
        ) as panel:
            console.print(panel)

        # Execute replay with progress
        if watch:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Executing replay...", total=None)

                try:
                    branch = await engine.replay(job)
                    progress.update(task, description="Replay completed!")

                except Exception as e:
                    progress.update(task, description=f"Replay failed: {e}")
                    console.print(f"[red]Error: {e}[/red]")
                    return
        else:
            try:
                branch = await engine.replay(job)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return

        # Show results
        result = {
            "job_id": job.job_id,
            "branch_id": branch.branch_id,
            "block_number": branch.block_number,
            "snapshot_id": branch.snapshot_id,
            "created_at": branch.created_at.isoformat(),
            "patches_applied": len(branch.patches_applied),
            "status": "completed",
        }

        console.print(f"[green]✓ Replay completed successfully![/green]")
        console.print(f"[cyan]Branch ID: {branch.branch_id}[/cyan]")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            # Pretty print JSON
            syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
            console.print(syntax)

    run_async(_replay())


@tm.command()
@click.argument("branch_id")
@click.option("--patch-file", "-f", help="JSON file with patches")
@click.option("--storage", help="Storage patch: address:slot:value")
@click.option("--balance", help="Balance patch: address:value")
@click.option("--code", help="Code patch: address:bytecode")
@click.option("--macro", help="Macro patch: macro_name:param1=value1,param2=value2")
@click.option("--output", "-o", help="Output file for new branch info")
@click.option("--validate", is_flag=True, help="Validate patches before applying")
def patch(branch_id, patch_file, storage, balance, code, macro, output, validate):
    """
    Apply patches to a branch.

    Examples:
        tm patch abc123 --storage 0x123:0x0:0x1
        tm patch abc123 --balance 0x456:1000000000000000000
        tm patch abc123 --macro disable_reentrancy:contract_address=0x123
        tm patch abc123 -f patches.json --validate
    """

    async def _patch():
        engine = await get_engine()

        # Build patches list
        patches = []

        # Load from file
        if patch_file:
            try:
                with open(patch_file, "r") as f:
                    file_patches = json.load(f)
                    patches.extend(file_patches)
                console.print(
                    f"[green]Loaded {len(file_patches)} patches from file[/green]"
                )
            except Exception as e:
                console.print(f"[red]Failed to load patch file: {e}[/red]")
                return

        # Add command line patches
        if storage:
            try:
                address, slot, value = storage.split(":")
                patches.append(
                    {
                        "type": "storage",
                        "address": address,
                        "slot": slot,
                        "value": value,
                        "description": f"CLI storage patch {slot}",
                    }
                )
            except ValueError:
                console.print(
                    "[red]Invalid storage format. Use: address:slot:value[/red]"
                )
                return

        if balance:
            try:
                address, value = balance.split(":")
                patches.append(
                    {
                        "type": "balance",
                        "address": address,
                        "value": value,
                        "description": f"CLI balance patch",
                    }
                )
            except ValueError:
                console.print("[red]Invalid balance format. Use: address:value[/red]")
                return

        if code:
            try:
                address, bytecode = code.split(":", 1)
                patches.append(
                    {
                        "type": "code",
                        "address": address,
                        "value": bytecode,
                        "description": f"CLI code patch",
                    }
                )
            except ValueError:
                console.print("[red]Invalid code format. Use: address:bytecode[/red]")
                return

        if macro:
            try:
                macro_name, params_str = macro.split(":", 1)
                params = {}
                for param in params_str.split(","):
                    key, value = param.split("=")
                    params[key.strip()] = value.strip()

                macro_patch = engine.patch_engine.expand_macro(macro_name, **params)
                patches.append(macro_patch)
                console.print(
                    f"[green]Expanded macro '{macro_name}' with {len(params)} parameters[/green]"
                )

            except Exception as e:
                console.print(f"[red]Failed to expand macro: {e}[/red]")
                return

        if not patches:
            console.print("[yellow]No patches specified[/yellow]")
            return

        # Validate patches if requested
        if validate:
            console.print("[cyan]Validating patches...[/cyan]")
            validation_errors = []
            for i, patch_data in enumerate(patches):
                try:
                    validation = engine.patch_engine.validate_patch(patch_data)
                    if not validation.valid:
                        validation_errors.extend(
                            [f"Patch {i}: {err}" for err in validation.errors]
                        )
                    if validation.warnings:
                        for warning in validation.warnings:
                            console.print(
                                f"[yellow]Warning - Patch {i}: {warning}[/yellow]"
                            )
                except Exception as e:
                    validation_errors.append(f"Patch {i}: {e}")

            if validation_errors:
                console.print("[red]Validation failed:[/red]")
                for error in validation_errors:
                    console.print(f"  [red]• {error}[/red]")
                return

            console.print("[green]✓ All patches valid[/green]")

        # Get source branch
        branch = engine.get_branch(branch_id)
        if not branch:
            console.print(f"[red]Branch {branch_id} not found[/red]")
            return

        # Apply patches
        console.print(
            f"[cyan]Applying {len(patches)} patches to branch {branch_id}...[/cyan]"
        )

        try:
            new_branch = await engine.patch(branch, patches)

            result = {
                "original_branch": branch_id,
                "new_branch": new_branch.branch_id,
                "patches_applied": len(patches),
                "block_number": new_branch.block_number,
                "snapshot_id": new_branch.snapshot_id,
                "created_at": new_branch.created_at.isoformat(),
            }

            console.print(f"[green]✓ Patches applied successfully![/green]")
            console.print(f"[cyan]New Branch ID: {new_branch.branch_id}[/cyan]")

            if output:
                with open(output, "w") as f:
                    json.dump(result, f, indent=2)
                console.print(f"[green]Results saved to {output}[/green]")
            else:
                syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
                console.print(syntax)

        except Exception as e:
            console.print(f"[red]Patch failed: {e}[/red]")

    run_async(_patch())


@tm.command()
@click.argument("from_branch")
@click.argument("to_branch")
@click.option(
    "--format",
    default="json",
    type=click.Choice(["json", "html", "text", "compact"]),
    help="Output format",
)
@click.option("--output", "-o", help="Output file for diff")
@click.option("--include-unchanged", is_flag=True, help="Include unchanged items")
def diff(from_branch, to_branch, format, output, include_unchanged):
    """
    Generate diff between two branches.

    Examples:
        tm diff branch1 branch2
        tm diff branch1 branch2 --format html -o diff.html
        tm diff branch1 branch2 --include-unchanged
    """

    async def _diff():
        engine = await get_engine()

        console.print(
            f"[cyan]Generating diff between {from_branch} and {to_branch}...[/cyan]"
        )

        try:
            diff_result = await engine.diff(from_branch, to_branch)

            # Format output based on format
            if format == "json":
                output_content = json.dumps(diff_result.to_dict(), indent=2)
            elif format == "text":
                output_content = _format_diff_text(diff_result)
            elif format == "compact":
                output_content = _format_diff_compact(diff_result)
            else:
                output_content = json.dumps(diff_result.to_dict(), indent=2)

            if output:
                with open(output, "w") as f:
                    f.write(output_content)
                console.print(f"[green]Diff saved to {output}[/green]")
            else:
                if format == "json":
                    syntax = Syntax(output_content, "json", theme="monokai")
                    console.print(syntax)
                else:
                    console.print(output_content)

        except Exception as e:
            console.print(f"[red]Diff generation failed: {e}[/red]")

    run_async(_diff())


def _format_diff_text(diff_result) -> str:
    """Format diff as plain text."""
    lines = [
        f"Diff: {diff_result.from_branch} → {diff_result.to_branch}",
        f"Generated: {diff_result.created_at}",
        "",
    ]

    if diff_result.storage_changes:
        lines.append("=== Storage Changes ===")
        for addr, changes in diff_result.storage_changes.items():
            lines.append(f"Address: {addr}")
            for slot, change in changes.items():
                old_val = change.get("old_value", "N/A")
                new_val = change.get("new_value", "N/A")
                lines.append(f"  Slot {slot}: {old_val} → {new_val}")
        lines.append("")

    if diff_result.balance_changes:
        lines.append("=== Balance Changes ===")
        for addr, change in diff_result.balance_changes.items():
            old_val = change.get("old_balance", "N/A")
            new_val = change.get("new_balance", "N/A")
            lines.append(f"Address {addr}: {old_val} → {new_val}")
        lines.append("")

    return "\n".join(lines)


def _format_diff_compact(diff_result) -> str:
    """Format diff compactly."""
    storage_count = len(diff_result.storage_changes)
    balance_count = len(diff_result.balance_changes)
    code_count = len(diff_result.code_changes)
    total_changes = storage_count + balance_count + code_count

    return f"Diff: {total_changes} changes ({storage_count} storage, {balance_count} balance, {code_count} code)"


@tm.command()
@click.option("--limit", default=20, help="Maximum branches to show")
@click.option(
    "--format",
    default="table",
    type=click.Choice(["table", "json", "simple"]),
    help="Output format",
)
def branches(limit, format):
    """
    List all branches.

    Examples:
        tm branches
        tm branches --limit 50 --format json
    """

    async def _branches():
        engine = await get_engine()

        branch_list = engine.list_branches()

        if not branch_list:
            console.print("[yellow]No branches found[/yellow]")
            return

        # Apply limit
        if limit:
            branch_list = branch_list[:limit]

        if format == "json":
            output = [branch.to_dict() for branch in branch_list]
            syntax = Syntax(json.dumps(output, indent=2), "json", theme="monokai")
            console.print(syntax)

        elif format == "simple":
            for branch in branch_list:
                console.print(
                    f"{branch.branch_id} - {branch.name} (Block {branch.block_number})"
                )

        else:  # table format
            table = Table(title="Branches")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Block", justify="right")
            table.add_column("Patches", justify="right")
            table.add_column("Parent", style="dim")
            table.add_column("Created", style="dim")

            for branch in branch_list:
                table.add_row(
                    branch.branch_id[:8] + "...",
                    branch.name or "Unnamed",
                    str(branch.block_number),
                    str(len(branch.patches_applied)),
                    (branch.parent_branch_id[:8] + "...")
                    if branch.parent_branch_id
                    else "None",
                    branch.created_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)

    run_async(_branches())


@tm.command()
@click.option("--limit", default=20, help="Maximum jobs to show")
@click.option("--status", help="Filter by job status")
def jobs(limit, status):
    """
    List replay jobs.

    Examples:
        tm jobs
        tm jobs --status running --limit 10
    """

    async def _jobs():
        engine = await get_engine()

        job_list = engine.list_jobs()

        # Filter by status
        if status:
            job_list = [job for job in job_list if job.status.value == status]

        if not job_list:
            console.print("[yellow]No jobs found[/yellow]")
            return

        # Apply limit
        if limit:
            job_list = job_list[:limit]

        table = Table(title="Replay Jobs")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("VM", style="blue")
        table.add_column("Block/TX", style="yellow")
        table.add_column("Created", style="dim")

        for job in job_list:
            block_tx = (
                job.tx_hash[:10] + "..."
                if job.tx_hash
                else str(job.block_number or "Range")
            )

            table.add_row(
                job.job_id[:8] + "...",
                job.name or "Unnamed",
                job.status.value,
                job.vm_backend.value,
                block_tx,
                job.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

    run_async(_jobs())


@tm.command()
def macros():
    """List available patch macros."""

    async def _macros():
        engine = await get_engine()

        macro_list = engine.patch_engine.list_macros()

        if not macro_list:
            console.print("[yellow]No macros available[/yellow]")
            return

        table = Table(title="Available Patch Macros")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="magenta")

        for macro in macro_list:
            table.add_row(macro["name"], macro["description"])

        console.print(table)

    run_async(_macros())


@tm.command()
def stats():
    """Show engine statistics."""

    async def _stats():
        engine = await get_engine()

        stats = engine.get_engine_stats()
        storage_stats = engine.snapshot_manager.get_storage_stats()

        # Create info panel
        info_text = f"""
[bold]Engine Statistics[/bold]

Branches: {stats['total_branches']}
Active Jobs: {stats['active_jobs']}
Forensic Sessions: {stats['forensic_sessions']}
Registered Plugins: {stats['registered_plugins']}
VM Backend: {stats['vm_backend']}

[bold]Storage Statistics[/bold]

Total Snapshots: {storage_stats['total_snapshots']}
Storage Size: {storage_stats['total_size_mb']:.2f} MB
Compression: {'Enabled' if storage_stats['compression_enabled'] else 'Disabled'}
Deduplication: {'Enabled' if storage_stats['deduplication_enabled'] else 'Disabled'}
        """.strip()

        panel = Panel(info_text, title="Time Machine Statistics", border_style="cyan")
        console.print(panel)

    run_async(_stats())


@tm.command()
@click.option("--max-age-days", default=30, help="Maximum age in days")
def cleanup(max_age_days):
    """Clean up old snapshots."""

    async def _cleanup():
        engine = await get_engine()

        console.print(
            f"[cyan]Cleaning up snapshots older than {max_age_days} days...[/cyan]"
        )

        try:
            deleted_count = await engine.cleanup_old_snapshots(max_age_days)
            console.print(f"[green]✓ Cleaned up {deleted_count} snapshots[/green]")
        except Exception as e:
            console.print(f"[red]Cleanup failed: {e}[/red]")

    run_async(_cleanup())


if __name__ == "__main__":
    tm()
