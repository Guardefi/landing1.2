$directories = @(
    "api\routes",
    "api\middleware",
    "core\engines",
    "core\analyzers",
    "models\ml_models\trained_models",
    "blockchain",
    "database\repositories",
    "config",
    "tests\unit",
    "tests\integration",
    "tests\fixtures",
    "docker",
    "scripts"
)

$basePath = "C:\Users\ADMIN\CascadeProjects\honeypot-detector"

foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    New-Item -ItemType Directory -Path $fullPath -Force
    Write-Host "Created directory: $fullPath"
}

Write-Host "Directory structure setup complete!"
