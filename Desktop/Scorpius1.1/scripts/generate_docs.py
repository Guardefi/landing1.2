import os
import json
import argparse
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yaml
from pathlib import Path

class APIEndpoint(BaseModel):
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict]
    responses: Dict[str, Dict]

class APIDocumentation:
    def __init__(self, app: FastAPI):
        """
        Initialize API documentation generator
        
        Args:
            app: FastAPI application instance
        """
        self.app = app
        self.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes
        )

    def generate_markdown(self) -> str:
        """Generate Markdown documentation"""
        markdown = f"# {self.openapi_schema['info']['title']}\n\n"
        markdown += f"**Version:** {self.openapi_schema['info']['version']}\n\n"
        markdown += f"**Description:** {self.openapi_schema['info']['description']}\n\n"

        for path, path_item in self.openapi_schema['paths'].items():
            for method, operation in path_item.items():
                endpoint = APIEndpoint(
                    path=path,
                    method=method.upper(),
                    summary=operation.get('summary', ''),
                    description=operation.get('description', ''),
                    parameters=operation.get('parameters', []),
                    responses=operation.get('responses', {})
                )

                markdown += f"## {endpoint.method} {endpoint.path}\n\n"
                markdown += f"**Summary:** {endpoint.summary}\n\n"
                markdown += f"**Description:** {endpoint.description}\n\n"

                if endpoint.parameters:
                    markdown += "### Parameters\n\n"
                    markdown += "| Name | Type | Required | Description |\n"
                    markdown += "|------|------|----------|-------------|\n"
                    for param in endpoint.parameters:
                        markdown += f"| {param['name']} | {param['schema']['type']} | {'Yes' if param.get('required') else 'No'} | {param.get('description', '')} |\n"

                if endpoint.responses:
                    markdown += "\n### Responses\n\n"
                    for status, response in endpoint.responses.items():
                        markdown += f"#### Status {status}\n\n"
                        markdown += f"**Description:** {response.get('description', '')}\n\n"
                        if 'content' in response and 'application/json' in response['content']:
                            markdown += "**Example Response:**\n\n"
                            markdown += "```json\n"
                            markdown += json.dumps(response['content']['application/json']['schema'], indent=2)
                            markdown += "\n```\n\n"

                markdown += "---\n\n"

        return markdown

    def generate_html(self) -> str:
        """Generate HTML documentation"""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=self.app.title + " - API Documentation"
        )

    def save_docs(self, output_dir: str) -> None:
        """
        Save documentation to files
        
        Args:
            output_dir: Directory to save documentation
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save OpenAPI JSON
        with open(output_path / "openapi.json", "w") as f:
            json.dump(self.openapi_schema, f, indent=2)

        # Save Markdown
        with open(output_path / "api.md", "w") as f:
            f.write(self.generate_markdown())

        # Save HTML
        with open(output_path / "index.html", "w") as f:
            f.write(self.generate_html())

def main():
    parser = argparse.ArgumentParser(description="API Documentation Generator")
    parser.add_argument("--output-dir", default="docs/api",
                       help="Output directory for documentation files")
    parser.add_argument("--title", default="Scorpius Platform API",
                       help="API title")
    parser.add_argument("--version", default="1.0.0",
                       help="API version")
    
    args = parser.parse_args()

    # Create FastAPI app
    app = FastAPI(
        title=args.title,
        version=args.version,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json"
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Create documentation generator
    doc_generator = APIDocumentation(app)
    
    # Save documentation
    doc_generator.save_docs(args.output_dir)
    
    print(f"Documentation generated successfully at {args.output_dir}")

if __name__ == "__main__":
    main()
