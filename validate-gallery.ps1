# Gallery Data Validation Script
# Validates gallery-data.json against local or S3 images

param (
    [switch]$UseS3,
    [switch]$Quiet
)

# Configuration
$CONFIG_FILE = "$PSScriptRoot\docs\js\config.js"
$JSON_FILE = "$PSScriptRoot\docs\gallery-data.json"
$LOCAL_IMAGE_PATH = "$PSScriptRoot\docs\images"
$GALLERY_SUBFOLDER = "gallery"

# Output functions
function Write-Success($message) {
    if (-not $Quiet) {
        $host.UI.RawUI.ForegroundColor = "Green"
        Write-Output "✓ $message"
        $host.UI.RawUI.ForegroundColor = "White"
    }
}

function Write-Info($message) {
    if (-not $Quiet) {
        Write-Output $message
    }
}

function Write-Error($message) {
    $host.UI.RawUI.ForegroundColor = "Red"
    Write-Output "✗ $message"
    $host.UI.RawUI.ForegroundColor = "White"
}

# Check if gallery-data.json is valid JSON
Write-Info "Checking if gallery-data.json is valid JSON..."

try {
    $jsonContent = Get-Content -Path $JSON_FILE -Raw | ConvertFrom-Json
    Write-Success "gallery-data.json is valid JSON"
}
catch {
    Write-Error "Error parsing gallery-data.json: $_"
    exit 1
}

# S3 configuration
$s3BucketUrl = ""
$s3Prefix = ""

# Read S3 config if needed
if ($UseS3) {
    try {
        $configContent = Get-Content -Path $CONFIG_FILE -Raw
        
        # Extract bucket URL - simple approach
        $configContent -match "bucketUrl:\s*'([^']+)'" | Out-Null
        $s3BucketUrl = $Matches[1]
        
        # Extract prefix - simple approach
        $configContent -match "prefix:\s*'([^']+)'" | Out-Null
        $s3Prefix = $Matches[1]
        
        Write-Info "Using S3 bucket: $s3BucketUrl"
        Write-Info "Using S3 prefix: $s3Prefix"
    }
    catch {
        Write-Error "Error reading config.js: $_"
        exit 1
    }
}

# Extract all image references from the JSON
$jsonImageRefs = @{}
$imageCount = 0

foreach ($category in $jsonContent.categories) {
    foreach ($image in $category.images) {
        $imageCount++
        $jsonImageRefs[$image.src] = $true
    }
}

Write-Info "Found $imageCount image references in gallery-data.json"

# Verify all referenced images exist
$missingFiles = @()

if ($UseS3) {
    Write-Info "Checking if all referenced images exist in S3..."
    
    foreach ($imageRef in $jsonImageRefs.Keys) {
        $imageUrl = "$s3BucketUrl/$s3Prefix$imageRef"
        
        try {
            # Check if image exists via HTTP HEAD request
            $response = Invoke-WebRequest -Uri $imageUrl -Method HEAD -UseBasicParsing -DisableKeepAlive -ErrorAction SilentlyContinue
            
            if ($response.StatusCode -ne 200) {
                $missingFiles += $imageRef
                Write-Error "Image missing from S3: $imageRef"
            }
        }
        catch {
            $missingFiles += $imageRef
            Write-Error "Image missing from S3: $imageRef"
        }
    }
}
else {
    Write-Info "Checking if all referenced images exist locally..."
    
    foreach ($imageRef in $jsonImageRefs.Keys) {
        $localPath = Join-Path $LOCAL_IMAGE_PATH $imageRef
        if (-not (Test-Path -Path $localPath)) {
            $missingFiles += $imageRef
            Write-Error "Image missing locally: $imageRef"
        }
    }
}

# Check for unreferenced images
$unreferencedFiles = @()

# Always check local gallery folder
Write-Info "Checking if all local gallery images are referenced in JSON..."

# Get gallery directory path
$galleryPath = Join-Path $LOCAL_IMAGE_PATH $GALLERY_SUBFOLDER

# Create gallery folder if missing
if (-not (Test-Path -Path $galleryPath)) {
    New-Item -ItemType Directory -Path $galleryPath -Force
    Write-Info "Created gallery directory at $galleryPath"
}

# Get all files from gallery folder
$localFiles = Get-ChildItem -Path $galleryPath -File -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($LOCAL_IMAGE_PATH.Length + 1).Replace("\", "/")
    $relativePath
}

# Check for unreferenced files
foreach ($file in $localFiles) {
    if (-not $jsonImageRefs.ContainsKey($file)) {
        $unreferencedFiles += $file
        Write-Error "Unreferenced image: $file"
    }
}

# Final results
$errorCount = $missingFiles.Count + $unreferencedFiles.Count

if ($errorCount -eq 0) {
    Write-Success "All validations passed! Gallery data is consistent with image files."
    exit 0
}
else {
    Write-Error "Validation failed with $errorCount errors"
    Write-Error "Missing files: $($missingFiles.Count)"
    Write-Error "Unreferenced files: $($unreferencedFiles.Count)"
    exit 1
}

# Extract all image references from the JSON
$jsonImageRefs = @{}
$imageCount = 0

foreach ($category in $jsonContent.categories) {
    foreach ($image in $category.images) {
        $imageCount++
        $jsonImageRefs[$image.src] = $true
    }
}

Write-Info "Found $imageCount image references in gallery-data.json"

# Check 2: Verify all referenced images exist
$missingFiles = @()

if ($UseS3) {
    Write-Info "Checking if all referenced images exist in S3..."
    
    foreach ($imageRef in $jsonImageRefs.Keys) {
        $imageUrl = "$s3BucketUrl/$s3Prefix$imageRef"
        
        try {
            # Use Invoke-WebRequest with the HEAD method to check if the file exists
            # -UseBasicParsing prevents IE engine dependency
            # -DisableKeepAlive improves performance for multiple requests
            # -Method HEAD only gets headers, not the full file
            $response = Invoke-WebRequest -Uri $imageUrl -Method HEAD -UseBasicParsing -DisableKeepAlive -ErrorAction SilentlyContinue
            
            if ($response.StatusCode -ne 200) {
                $missingFiles += $imageRef
                Write-Error "Image referenced in JSON but missing from S3: $imageRef (HTTP Status: $($response.StatusCode))"
            }
        }
        catch {
            $missingFiles += $imageRef
            Write-Error "Image referenced in JSON but missing from S3: $imageRef (Error: $($_.Exception.Message))"
        }
    }
}
else {
    Write-Info "Checking if all referenced images exist locally..."
    
    foreach ($imageRef in $jsonImageRefs.Keys) {
        $localPath = Join-Path $LOCAL_IMAGE_PATH $imageRef
        if (-not (Test-Path -Path $localPath)) {
            $missingFiles += $imageRef
            Write-Error "Image referenced in JSON but missing locally: $imageRef"
        }
    }
}

# Check 3: Verify all files have corresponding entries in JSON
$unreferencedFiles = @()

# Always check local images for consistency, regardless of whether we're validating against S3 or not
Write-Info "Checking if all local gallery images are referenced in JSON..."

# Get all files from local gallery directory
$galleryPath = Join-Path $LOCAL_IMAGE_PATH $GALLERY_SUBFOLDER

# Create the gallery folder if it doesn't exist
if (-not (Test-Path -Path $galleryPath)) {
    New-Item -ItemType Directory -Path $galleryPath -Force
    Write-Info "Created local gallery directory at $galleryPath"
}

# Get all files from local gallery folder
$localFiles = Get-ChildItem -Path $galleryPath -File -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($LOCAL_IMAGE_PATH.Length + 1).Replace("\", "/")
    $relativePath
}

# Check for unreferenced files
foreach ($file in $localFiles) {
    if (-not $jsonImageRefs.ContainsKey($file)) {
        $unreferencedFiles += $file
        Write-Error "Image exists in local gallery folder but not referenced in JSON: $file"
    }
}

# Summary
$errorCount = $missingFiles.Count + $unreferencedFiles.Count

if ($errorCount -eq 0) {
    Write-Success "All validations passed! Gallery data is consistent with image files."
    exit 0
}
else {
    Write-Error "Validation failed with $errorCount errors:"
    Write-Error "- Missing files: $($missingFiles.Count)" 
    Write-Error "- Unreferenced files: $($unreferencedFiles.Count)"
    exit 1
}
