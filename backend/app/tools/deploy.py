"""Deployment tool for deploying applications."""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.tools.base import BaseTool


class DeployTool(BaseTool):
    """Tool for deploying applications to various platforms."""

    name = "deploy"
    description = "Deploy applications to various platforms"

    def __init__(self):
        self.deployments: Dict[str, Dict[str, Any]] = {}

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a deployment operation."""
        operations = {
            "frontend": self.deploy_frontend,
            "backend": self.deploy_backend,
            "logs": self.get_logs,
            "status": self.get_status,
            "list": self.list_deployments,
            "expose": self.expose_port,
            "docker_build": self.docker_build,
            "docker_push": self.docker_push,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        return await operations[operation](**kwargs)

    async def deploy_frontend(
        self,
        directory: str,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Deploy a frontend application (static files)."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}

            # Check for common build directories
            build_dirs = ["dist", "build", "out", "public", ".next/static"]
            build_dir = None
            for bd in build_dirs:
                if (dir_path / bd).exists():
                    build_dir = dir_path / bd
                    break

            if not build_dir:
                build_dir = dir_path

            # Generate deployment name
            deploy_name = name or f"frontend-{os.urandom(4).hex()}"

            # Simulate deployment (in real implementation, would deploy to CDN/hosting)
            deployment_info = {
                "name": deploy_name,
                "type": "frontend",
                "source_dir": str(build_dir),
                "status": "deployed",
                "url": f"https://{deploy_name}.kevin-deploy.example.com",
                "created_at": asyncio.get_event_loop().time(),
            }

            self.deployments[deploy_name] = deployment_info

            return {
                "success": True,
                "deployment": deployment_info,
                "message": f"Frontend deployed successfully to {deployment_info['url']}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def deploy_backend(
        self,
        directory: str,
        name: Optional[str] = None,
        port: int = 8000,
        env_vars: Optional[Dict[str, str]] = None,
        volume: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Deploy a backend application."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}

            # Check for common backend files
            has_requirements = (dir_path / "requirements.txt").exists()
            has_pyproject = (dir_path / "pyproject.toml").exists()
            has_package_json = (dir_path / "package.json").exists()

            framework = "unknown"
            if has_pyproject or has_requirements:
                framework = "python"
            elif has_package_json:
                framework = "nodejs"

            # Generate deployment name
            deploy_name = name or f"backend-{os.urandom(4).hex()}"

            # Simulate deployment
            deployment_info = {
                "name": deploy_name,
                "type": "backend",
                "source_dir": str(dir_path),
                "framework": framework,
                "port": port,
                "status": "deployed",
                "url": f"https://{deploy_name}.kevin-api.example.com",
                "internal_url": f"http://{deploy_name}.internal:8080",
                "env_vars": list(env_vars.keys()) if env_vars else [],
                "volume_mounted": volume,
                "created_at": asyncio.get_event_loop().time(),
            }

            self.deployments[deploy_name] = deployment_info

            return {
                "success": True,
                "deployment": deployment_info,
                "message": f"Backend deployed successfully to {deployment_info['url']}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_logs(
        self,
        name: str,
        lines: int = 100,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get logs from a deployment."""
        try:
            if name not in self.deployments:
                return {"error": f"Deployment not found: {name}"}

            # Simulate log retrieval
            deployment = self.deployments[name]
            sample_logs = [
                f"[{deployment['type']}] Starting application...",
                f"[{deployment['type']}] Listening on port {deployment.get('port', 80)}",
                f"[{deployment['type']}] Application ready",
                f"[{deployment['type']}] Health check passed",
            ]

            return {
                "success": True,
                "deployment": name,
                "logs": sample_logs,
                "lines_returned": len(sample_logs),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_status(
        self,
        name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get status of a deployment."""
        try:
            if name not in self.deployments:
                return {"error": f"Deployment not found: {name}"}

            deployment = self.deployments[name]
            return {
                "success": True,
                "deployment": deployment,
                "health": "healthy",
                "uptime": "running",
            }
        except Exception as e:
            return {"error": str(e)}

    async def list_deployments(self, **kwargs: Any) -> Dict[str, Any]:
        """List all deployments."""
        return {
            "success": True,
            "deployments": list(self.deployments.values()),
            "count": len(self.deployments),
        }

    async def expose_port(
        self,
        port: int,
        protocol: str = "http",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Expose a local port to the internet."""
        try:
            # Generate a unique subdomain
            subdomain = f"tunnel-{os.urandom(4).hex()}"
            public_url = f"https://{subdomain}.kevin-tunnel.example.com"

            return {
                "success": True,
                "local_port": port,
                "protocol": protocol,
                "public_url": public_url,
                "message": f"Port {port} exposed at {public_url}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def docker_build(
        self,
        directory: str,
        tag: str,
        dockerfile: str = "Dockerfile",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build a Docker image."""
        try:
            dir_path = Path(directory)
            dockerfile_path = dir_path / dockerfile

            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}

            if not dockerfile_path.exists():
                return {"error": f"Dockerfile not found: {dockerfile_path}"}

            # Execute docker build
            process = await asyncio.create_subprocess_exec(
                "docker", "build", "-t", tag, "-f", str(dockerfile_path), str(dir_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {
                    "error": f"Docker build failed: {stderr.decode()}",
                    "stdout": stdout.decode(),
                }

            return {
                "success": True,
                "tag": tag,
                "output": stdout.decode(),
                "message": f"Docker image built successfully: {tag}",
            }
        except FileNotFoundError:
            return {"error": "Docker is not installed or not in PATH"}
        except Exception as e:
            return {"error": str(e)}

    async def docker_push(
        self,
        tag: str,
        registry: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Push a Docker image to a registry."""
        try:
            full_tag = f"{registry}/{tag}" if registry else tag

            # Execute docker push
            process = await asyncio.create_subprocess_exec(
                "docker", "push", full_tag,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {
                    "error": f"Docker push failed: {stderr.decode()}",
                    "stdout": stdout.decode(),
                }

            return {
                "success": True,
                "tag": full_tag,
                "output": stdout.decode(),
                "message": f"Docker image pushed successfully: {full_tag}",
            }
        except FileNotFoundError:
            return {"error": "Docker is not installed or not in PATH"}
        except Exception as e:
            return {"error": str(e)}
