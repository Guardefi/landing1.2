import os
import sys
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path
from core.backup.manager import BackupManager

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/var/log/scorpius/backup.log')
        ]
    )

def load_config(config_path: str) -> dict:
    """Load backup configuration"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        raise

def create_backup(service: str, config: dict) -> str:
    """
    Create a backup for a specific service
    
    Args:
        service: Name of the service to backup
        config: Backup configuration
        
    Returns:
        Backup ID
    """
    try:
        manager = BackupManager(config)
        backup_id = manager.create_backup(service)
        logger.info(f"Successfully created backup {backup_id} for {service}")
        return backup_id
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        raise

def restore_backup(service: str, backup_id: str, config: dict) -> None:
    """
    Restore a backup for a specific service
    
    Args:
        service: Name of the service to restore
        backup_id: ID of the backup to restore
        config: Backup configuration
    """
    try:
        manager = BackupManager(config)
        manager.restore_backup(service, backup_id)
        logger.info(f"Successfully restored backup {backup_id} for {service}")
    except Exception as e:
        logger.error(f"Failed to restore backup: {str(e)}")
        raise

def list_backups(service: str, config: dict, limit: int = 10) -> list:
    """
    List available backups for a service
    
    Args:
        service: Name of the service
        config: Backup configuration
        limit: Maximum number of backups to return
        
    Returns:
        List of backup IDs
    """
    try:
        manager = BackupManager(config)
        backups = manager.list_backups(service, limit)
        logger.info(f"Found {len(backups)} backups for {service}")
        return backups
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
        raise

def cleanup_old_backups(config: dict) -> None:
    """Clean up old backups based on retention policy"""
    try:
        manager = BackupManager(config)
        manager.cleanup_old_backups()
        logger.info("Successfully cleaned up old backups")
    except Exception as e:
        logger.error(f"Failed to clean up old backups: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Scorpius Backup System")
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Create backup command
    create_parser = subparsers.add_parser('create', help='Create a backup')
    create_parser.add_argument('--service', required=True, help='Service name')
    create_parser.add_argument('--config', default='config/backup_config.yaml', help='Config file path')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore a backup')
    restore_parser.add_argument('--service', required=True, help='Service name')
    restore_parser.add_argument('--backup-id', required=True, help='Backup ID to restore')
    restore_parser.add_argument('--config', default='config/backup_config.yaml', help='Config file path')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--service', required=True, help='Service name')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of backups to list')
    list_parser.add_argument('--config', default='config/backup_config.yaml', help='Config file path')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--config', default='config/backup_config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Execute command
        if args.command == 'create':
            create_backup(args.service, config)
        elif args.command == 'restore':
            restore_backup(args.service, args.backup_id, config)
        elif args.command == 'list':
            backups = list_backups(args.service, config, args.limit)
            print("\nAvailable backups:")
            for backup in backups:
                print(backup)
        elif args.command == 'cleanup':
            cleanup_old_backups(config)
        
    except Exception as e:
        logger.error(f"Backup operation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
