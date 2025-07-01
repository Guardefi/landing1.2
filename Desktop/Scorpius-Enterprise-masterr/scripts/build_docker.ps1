# build_docker.ps1 — Guardefi service builder / pusher
# -----------------------------------------------------------------------------
# Usage:   ./scripts/build_docker.ps1   (from repo root or scripts/)
# Requires: PowerShell 5.1+ (7+ recommended), Docker Desktop, `yq` in PATH.

# -----------------------------------------------------------------------------
# GLOBALS & ERROR HANDLING
# -----------------------------------------------------------------------------
$Global:PSDefaultParameterValues['*:ErrorAction'] = 'Stop'
Clear-Host

# -----------------------------------------------------------------------------
# LOAD CONFIG
# -----------------------------------------------------------------------------
$configFile = Join-Path $PSScriptRoot '..\config\docker_build.yaml'
if (-not (Test-Path $configFile)) { throw "Config not found: $configFile" }
$cfg = yq e -o json '.' $configFile | ConvertFrom-Json

foreach ($key in 'registry', 'organization', 'version', 'services') {
    if (-not $cfg.$key) { throw "$key missing in config" }
}

$REGISTRY = $cfg.registry
$ORG = $cfg.organization
$VER = $cfg.version
$SERVICES = $cfg.services

Write-Host "Registry     : $REGISTRY"
Write-Host "Organization : $ORG"
Write-Host "Version      : $VER"
Write-Host "Services     : $($SERVICES.name -join ', ')"

# -----------------------------------------------------------------------------
# DOCKER HUB LOGIN (if needed)
# -----------------------------------------------------------------------------
if ($REGISTRY -eq 'docker.io') {
    $user = try { docker info --format '{{ .AuthConfig.Username }}' 2>$null } catch { '' }
    if (-not $user) {
        Write-Host "Docker Hub PAT required for $ORG" -ForegroundColor Yellow
        $secure = Read-Host -Prompt 'Enter Docker PAT' -AsSecureString
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        $pat = [Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        $pat | docker login -u $ORG --password-stdin
        if ($LASTEXITCODE -ne 0) { throw 'Docker login failed' }
    }
    else {
        Write-Host "Already logged in as $user" -ForegroundColor Green
    }
}

# -----------------------------------------------------------------------------
# HELPER: BUILD + PUSH ONE IMAGE
# -----------------------------------------------------------------------------
function Build-Push-Service {
    param(
        [psobject]$SvcObj,
        [string[]]$SearchPaths
    )

    $name = $SvcObj.name
    $rel = $SvcObj.path

    # locate Docker context
    $ctx = $null
    foreach ($base in $SearchPaths) {
        $try = Join-Path $base $rel
        if (Test-Path $try) { $ctx = $try; break }
    }
    if (-not $ctx) { Write-Warning "Path not found for $name"; return }
    if (-not (Test-Path (Join-Path $ctx 'Dockerfile'))) { Write-Warning "Dockerfile missing for $name"; return }
    if (-not (Test-Path (Join-Path $ctx 'entrypoint.sh'))) { Write-Warning "entrypoint.sh missing for $name"; return }

    # Handle docker.io special case
    if ($REGISTRY -eq 'docker.io') {
        $image = "{0}/{1}:{2}" -f $ORG, $name, $VER
    } else {
        $image = "{0}/{1}/{2}:{3}" -f $REGISTRY, $ORG, $name, $VER
    }

    # skip build if already exists locally
    $exists = docker images --format '{{.Repository}}:{{.Tag}}' | Where-Object { $_ -eq $image }
    if ($exists) { Write-Host "$name already built - skipping"; return }

    # BUILD
    Write-Host "\n--- Building $image ---" -ForegroundColor Cyan
    docker build --progress=plain -t $image $ctx
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $name" }

    # PUSH WITH RETRY
    $retry = 0
    while ($retry -lt 3) {
        docker push $image
        if ($LASTEXITCODE -eq 0) { break }
        $retry++
        Write-Warning "Push failed ($retry/3) for $name — retrying in 5s"; Start-Sleep 5
    }
    if ($LASTEXITCODE -ne 0) { throw "Push failed: $name" }

    # TAG :latest
    if ($REGISTRY -eq 'docker.io') {
        $latest = "{0}:{1}" -f $ORG, $name
    } else {
        $latest = "{0}/{1}/{2}" -f $REGISTRY, $ORG, $name
    }
    docker tag $image "$latest:latest"
    docker push "$latest:latest" | Out-Null

    # EXTRA TAGS
    if ($SvcObj.tags) {
        foreach ($tag in $SvcObj.tags) {
            if ($tag -match '^(latest|' + [regex]::Escape($VER) + ')$') { continue }
            if ($tag -notmatch '^[A-Za-z0-9_.-]+$') { Write-Warning "Invalid tag '$tag' skipped for $name"; continue }
            if ($REGISTRY -eq 'docker.io') {
                $extra = "{0}/{1}:{2}" -f $ORG, $name, $tag
            } else {
                $extra = "{0}/{1}/{2}:{3}" -f $REGISTRY, $ORG, $name, $tag
            }
            docker tag $image $extra
            docker push $extra | Out-Null
        }
    }

    Write-Host "✓ Finished $name" -ForegroundColor Green
}
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
$repoRoot = Split-Path -Parent $PSScriptRoot
$search = @($repoRoot, "$repoRoot/services", "$repoRoot/backend", "$repoRoot/frontend")

foreach ($svc in $SERVICES) {
    Build-Push-Service -SvcObj $svc -SearchPaths $search
}

Write-Host "\nAll services processed." -ForegroundColor Green