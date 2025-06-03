# Gallery Validation
param (
  [switch]$UseS3,
  [switch]$Quiet
)

# Paths
$JSON_FILE = "$PSScriptRoot\docs\gallery-data.json"
$LOCAL_IMAGE_PATH = "$PSScriptRoot\docs\images"
$GALLERY_SUBFOLDER = "gallery"

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

Write-Info "Checking if referenced images exist locally"
foreach ($imageRef in $jsonImageRefs.Keys) {
  $localPath = Join-Path $LOCAL_IMAGE_PATH $imageRef
  if (-not (Test-Path -Path $localPath)) {
    $missingFiles += $imageRef
    Write-ValidationError "Missing: $imageRef"
  }
}

# Check for unreferenced images
$unreferencedFiles = @()
$galleryPath = Join-Path $LOCAL_IMAGE_PATH $GALLERY_SUBFOLDER

if (-not (Test-Path -Path $galleryPath)) {
  New-Item -ItemType Directory -Path $galleryPath -Force
  Write-Info "Created gallery directory"
}

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

# Results
$errorCount = $missingFiles.Count + $unreferencedFiles.Count

if ($errorCount -eq 0) {
  Write-Success "All validations passed!"
  exit 0
}
else {
  Write-ValidationError "Validation failed with $errorCount errors"
  exit 1
}
