# Gallery Validation
param (
  [switch]$UseS3,
  [switch]$Quiet
)

# Paths
$JSON_FILE = "$PSScriptRoot\docs\gallery-data.json"
$LOCAL_IMAGE_PATH = "$PSScriptRoot\docs\images"
$GALLERY_SUBFOLDER = "gallery"
$CONFIG_FILE = "$PSScriptRoot\docs\js\config.js"

# Simple output functions
function Write-Success {
  param($message)
  Write-Output "SUCCESS: $message"
}

function Write-Info {
  param($message) 
  if (-not $Quiet) { Write-Output "INFO: $message" }
}

function Write-ValidationError {
  param($message)
  Write-Output "ERROR: $message"
}

function Test-S3File {
  param($url)
  try {
    $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
    return $response.StatusCode -eq 200
  }
  catch {
    return $false
  }
}

# Validate JSON
Write-Info "Checking gallery-data.json"
try {
  $jsonContent = Get-Content -Path $JSON_FILE -Raw | ConvertFrom-Json
  Write-Success "gallery-data.json is valid JSON"
}
catch {
  Write-ValidationError "Invalid JSON in gallery-data.json"
  exit 1
}

# Extract image references
$jsonImageRefs = @{}
$imageCount = 0
foreach ($category in $jsonContent.categories) {
  foreach ($image in $category.images) {
    $imageCount++
    $jsonImageRefs[$image.src] = $true
  }
}
Write-Info "Found $imageCount image references"

# Check if referenced images exist
$missingFiles = @()

if ($UseS3) {
  Write-Info "Validating against S3 bucket"
  try {
    $configContent = Get-Content -Path $CONFIG_FILE -Raw
    $configContent -match "bucketUrl:\s*'([^']+)'" | Out-Null
    $bucketUrl = $Matches[1]
    $configContent -match "prefix:\s*'([^']+)'" | Out-Null
    $prefix = $Matches[1]
    if (-not $bucketUrl -or -not $prefix) {
      throw "Could not extract S3 configuration from config.js"
    }
    $baseUrl = $bucketUrl.TrimEnd('/') + '/' + $prefix.Trim('/') + '/'
    Write-Info "Using S3 base URL: $baseUrl"
    foreach ($imageRef in $jsonImageRefs.Keys) {
      $imageUrl = $baseUrl + $imageRef
      if (-not (Test-S3File -url $imageUrl)) {
        $missingFiles += $imageRef
        Write-ValidationError "Missing in S3: $imageRef"
      }
    }
  }
  catch {
    Write-ValidationError "Error during S3 validation: $_"
    exit 1
  }
} else {
  Write-Info "Validating against local files"
  foreach ($imageRef in $jsonImageRefs.Keys) {
    $localPath = Join-Path $LOCAL_IMAGE_PATH $imageRef
    if (-not (Test-Path -Path $localPath)) {
      $missingFiles += $imageRef
      Write-ValidationError "Missing locally: $imageRef"
    }
  }
}

# Always check for unreferenced local images
$unreferencedFiles = @()
$galleryPath = Join-Path $LOCAL_IMAGE_PATH $GALLERY_SUBFOLDER
if (Test-Path -Path $galleryPath) {
  $localFiles = Get-ChildItem -Path $galleryPath -File -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($LOCAL_IMAGE_PATH.Length + 1).Replace("\", "/")
    $relativePath
  }
  foreach ($file in $localFiles) {
    if (-not $jsonImageRefs.ContainsKey($file)) {
      $unreferencedFiles += $file
      Write-ValidationError "Unreferenced: $file"
    }
  }
}

# Results
$errorCount = $missingFiles.Count + $unreferencedFiles.Count
if ($errorCount -eq 0) {
  $location = if ($UseS3) { "S3 bucket" } else { "local files" }
  Write-Success "All validations passed against $location!"
  exit 0
} else {
  $location = if ($UseS3) { "S3 bucket" } else { "local files" }
  Write-ValidationError "Validation against $location failed with $errorCount errors"
  exit 1
}
