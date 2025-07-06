import os
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
import docker
from kubernetes import client, config

logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self, environment: str = "production"):
        """
        Initialize deployment manager
        
        Args:
            environment: Target environment (production, staging, development)
        """
        self.environment = environment
        self.docker_client = docker.from_env()
        self.k8s_config = config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        self.k8s_apps_client = client.AppsV1Api()
        self.services = [
            "api-gateway",
            "bridge-service",
            "mempool",
            "honeypot",
            "quantum",
            "scanner"
        ]

    def build_images(self) -> None:
        """Build Docker images for all services"""
        logger.info("Starting image builds...")
        
        for service in self.services:
            logger.info(f"Building image for {service}...")
            try:
                image_name = f"scorpius/{service}:latest"
                build_path = f"services/{service}"
                
                # Build the image
                self.docker_client.images.build(
                    path=build_path,
                    tag=image_name,
                    rm=True,
                    pull=True
                )
                
                # Tag for registry
                registry_image = f"registry.example.com/{image_name}"
                self.docker_client.images.get(image_name).tag(registry_image)
                
                # Push to registry
                self.docker_client.images.push(registry_image)
                
                logger.info(f"Successfully built and pushed {service}")
            except Exception as e:
                logger.error(f"Failed to build {service}: {str(e)}")
                raise

    def deploy_to_k8s(self) -> None:
        """Deploy services to Kubernetes"""
        logger.info("Starting Kubernetes deployment...")
        
        # Create namespace if it doesn't exist
        namespace = self.environment
        try:
            self.k8s_client.create_namespace(
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=namespace)
                )
            )
        except client.exceptions.ApiException as e:
            if e.status != 409:  # Namespace already exists
                raise

        # Deploy services
        for service in self.services:
            logger.info(f"Deploying {service}...")
            
            # Read deployment YAML
            deployment_path = Path("infrastructure/k8s") / self.environment / f"{service}.yaml"
            with open(deployment_path, "r") as f:
                deployment_yaml = f.read()
            
            # Apply deployment
            try:
                k8s_objects = yaml.safe_load_all(deployment_yaml)
                for obj in k8s_objects:
                    kind = obj.get("kind")
                    name = obj.get("metadata", {}).get("name")
                    
                    if kind == "Deployment":
                        self.k8s_apps_client.create_namespaced_deployment(
                            namespace=namespace,
                            body=obj
                        )
                    elif kind == "Service":
                        self.k8s_client.create_namespaced_service(
                            namespace=namespace,
                            body=obj
                        )
                    
                logger.info(f"Successfully deployed {service}")
            except Exception as e:
                logger.error(f"Failed to deploy {service}: {str(e)}")
                raise

    def verify_deployment(self) -> None:
        """Verify deployment status"""
        logger.info("Verifying deployment status...")
        
        for service in self.services:
            try:
                # Check deployment status
                deployment = self.k8s_apps_client.read_namespaced_deployment(
                    name=service,
                    namespace=self.environment
                )
                
                # Check pods
                pods = self.k8s_client.list_namespaced_pod(
                    namespace=self.environment,
                    label_selector=f"app={service}"
                )
                
                logger.info(f"{service} status:")
                logger.info(f"  Replicas: {deployment.status.replicas}")
                logger.info(f"  Available: {deployment.status.available_replicas}")
                logger.info(f"  Pods: {len(pods.items)}")
                
                for pod in pods.items:
                    logger.info(f"  Pod {pod.metadata.name}:")
                    logger.info(f"    Status: {pod.status.phase}")
                    logger.info(f"    Ready: {pod.status.container_statuses[0].ready}")
                
            except Exception as e:
                logger.error(f"Failed to verify {service}: {str(e)}")
                raise

    def rollback(self, version: str) -> None:
        """Rollback deployment to previous version"""
        logger.info(f"Rolling back to version {version}...")
        
        for service in self.services:
            try:
                self.k8s_apps_client.rollback_namespaced_deployment(
                    name=service,
                    namespace=self.environment,
                    body=client.AppsV1DeploymentRollback(
                        name=service,
                        rolled_back_to_revision=version
                    )
                )
                logger.info(f"Successfully rolled back {service} to version {version}")
            except Exception as e:
                logger.error(f"Failed to rollback {service}: {str(e)}")
                raise

def main():
    parser = argparse.ArgumentParser(description="Scorpius Platform Deployment Manager")
    parser.add_argument("--environment", default="production",
                       help="Target environment (production, staging, development)")
    parser.add_argument("--action", required=True,
                       choices=["build", "deploy", "verify", "rollback"],
                       help="Action to perform")
    parser.add_argument("--version", help="Version to rollback to")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize deployment manager
    manager = DeploymentManager(args.environment)
    
    try:
        if args.action == "build":
            manager.build_images()
        elif args.action == "deploy":
            manager.deploy_to_k8s()
        elif args.action == "verify":
            manager.verify_deployment()
        elif args.action == "rollback":
            if not args.version:
                raise ValueError("--version is required for rollback")
            manager.rollback(args.version)
        
        logger.info("Deployment completed successfully")
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
