#!/usr/bin/env python3
"""
Lambda Deployment Package Creator

This script creates deployment packages for AWS Lambda by:
1. Creating two separate zip files for Lambda deployment:
   - app.zip: Contains the Lambda function code from the 'lambda' directory
   - dependencies.zip: Contains the Python dependencies from the 'packaging/_dependencies' directory
2. The dependencies are packaged with the correct directory structure for Lambda layer deployment
3. Any existing zip files are removed before creating new ones
4. Both zip files are stored in the 'packaging' directory for CDK to use during deployment

Note: This script assumes dependencies have already been installed to the 'packaging/_dependencies' 
directory using the pip command with the appropriate platform flag.
"""

import os
import zipfile
from pathlib import Path

def create_lambda_package():
    # Define paths
    current_dir = Path.cwd()
    packaging_dir = current_dir / "packaging"

    # get the path to the strands_tools package
    weather_app_dir = current_dir / "lambda" / "weather"
    query_dir = current_dir / "lambda" / "query"
    weather_app_deployment_zip = packaging_dir / "weather_app.zip"
    query_app_deployment_zip = packaging_dir / "query_app.zip"

    dependencies_dir = packaging_dir / "_dependencies"
    dependencies_deployment_zip = packaging_dir / "dependencies.zip"

    print(f"Creating Lambda deployment package: {weather_app_deployment_zip}")
    print(f"Creating Lambda deployment package: {query_app_deployment_zip}")


    # Clean up any existing package directory or zip file
    if weather_app_deployment_zip.exists():
        os.remove(weather_app_deployment_zip)
    
    # Clean up any existing package directory or zip file
    if query_app_deployment_zip.exists():
        os.remove(query_app_deployment_zip)

    if dependencies_deployment_zip.exists():
        os.remove(dependencies_deployment_zip)

    # Create ZIP file
    print("Creating ZIP files...")
    os.makedirs(weather_app_deployment_zip.parent, exist_ok=True)
    os.makedirs(query_app_deployment_zip.parent, exist_ok=True)

    print(f"  Creating {dependencies_deployment_zip.name}...")
    with zipfile.ZipFile(dependencies_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dependencies_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = Path("python") / os.path.relpath(file_path, dependencies_dir)
                zipf.write(file_path, arcname)

    print(f"  Creating {weather_app_deployment_zip.name}...")
    with zipfile.ZipFile(weather_app_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(weather_app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, weather_app_dir)
                zipf.write(file_path, arcname)
    print(f"  Creating {query_app_deployment_zip.name}...")
    with zipfile.ZipFile(query_app_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(query_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, query_dir)
                zipf.write(file_path, arcname)

    print(f"Lambda deployment packages created successfully: {dependencies_deployment_zip.name} {weather_app_deployment_zip.name} {query_app_deployment_zip.name}")
    return True


if __name__ == "__main__":
    create_lambda_package()