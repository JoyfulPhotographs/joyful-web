# PowerShell script to upload local images to Amazon S3
# Prerequisites: AWS CLI installed and configured

# Configuration
$LOCAL_IMAGE_PATH = "$PSScriptRoot\docs\images"
$S3_BUCKET = "photos-joyfulphotographs-com"  # S3 bucket name for images
$S3_PREFIX = "website-images/"  # Prefix within bucket
$AWS_PROFILE = "joyful-photos"  # AWS profile to use (from ~/.aws/credentials)

# Check if the local directory exists
if (-not (Test-Path -Path $LOCAL_IMAGE_PATH)) {
    Write-Host "✗ Error: Local images directory not found at $LOCAL_IMAGE_PATH" -ForegroundColor Red
    Write-Host "Please ensure the directory exists before running this script" -ForegroundColor Yellow
    exit 1
}

# Main purpose: Upload local images to S3
Write-Host "Preparing to upload local images to S3"

# Ask for confirmation
$uploadChoice = Read-Host "Do you want to upload local images to S3? (y/n)"
if ($uploadChoice -eq "y") {
    Write-Host "Uploading images to S3..."
    # No ACL flag since bucket has Object Ownership set to "Bucket owner enforced"
    aws s3 sync $LOCAL_IMAGE_PATH "s3://$S3_BUCKET/$S3_PREFIX" --profile $AWS_PROFILE
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully uploaded images to S3!" -ForegroundColor Green
    } else {
        Write-Host "✗ Error uploading images to S3" -ForegroundColor Red
        exit 1
    }
    
    # Generate URLs file
    $baseUrl = "https://$S3_BUCKET.s3.amazonaws.com/$S3_PREFIX"
    $urlsFile = "$PSScriptRoot\s3-image-urls.txt"
    
    Write-Host "Generating image URLs file at $urlsFile"
    
    # Create header for URL file
    "# S3 Image URLs - Generated $(Get-Date)" | Out-File -FilePath $urlsFile
    "# Base URL: $baseUrl" | Out-File -FilePath $urlsFile -Append
    "# Format in config.js: s3.getImageUrl('filename.jpg')" | Out-File -FilePath $urlsFile -Append
    "" | Out-File -FilePath $urlsFile -Append
    
    # Get a list of all images in the local directory
    $imageCount = 0
    Get-ChildItem -Path $LOCAL_IMAGE_PATH -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($LOCAL_IMAGE_PATH.Length + 1).Replace("\", "/")
        "$baseUrl$relativePath - $relativePath" | Out-File -FilePath $urlsFile -Append
        $imageCount++
    }
    
    Write-Host "\nImage Upload Summary:" -ForegroundColor Cyan
    Write-Host "- Total images processed: $imageCount" 
    Write-Host "- S3 bucket: $S3_BUCKET"
    Write-Host "- S3 prefix: $S3_PREFIX"
    Write-Host "- URL list saved to: $urlsFile"
    Write-Host "- Base URL: $baseUrl"
    
    Write-Host "\nDone!" -ForegroundColor Green
}
else {
    Write-Host "Upload cancelled by user" -ForegroundColor Yellow
}

Write-Host "Sync complete!"
