# PowerShell script to sync local images with Amazon S3
# Prerequisites: AWS CLI installed and configured

# Configuration
$LOCAL_IMAGE_PATH = "$PSScriptRoot\docs\images"
$S3_BUCKET = "photos-joyfulphotographs-com"  # S3 bucket name for images
$S3_PREFIX = "website-images/"  # Prefix within bucket
$AWS_PROFILE = "joyful-photos"  # AWS profile to use (from ~/.aws/credentials)

# Ensure the local directory exists
if (-not (Test-Path -Path $LOCAL_IMAGE_PATH)) {
    New-Item -ItemType Directory -Path $LOCAL_IMAGE_PATH -Force
    Write-Host "Created local images directory at $LOCAL_IMAGE_PATH"
}

# Sync from S3 to local (download any new or updated images)
Write-Host "Downloading images from S3..."
aws s3 sync "s3://$S3_BUCKET/$S3_PREFIX" $LOCAL_IMAGE_PATH --delete --profile $AWS_PROFILE

# Ask if user wants to upload local changes to S3
$uploadChoice = Read-Host "Do you want to upload local images to S3? (y/n)"
if ($uploadChoice -eq "y") {
    Write-Host "Uploading images to S3..."
    aws s3 sync $LOCAL_IMAGE_PATH "s3://$S3_BUCKET/$S3_PREFIX" --acl public-read --profile $AWS_PROFILE
    
    # Generate URLs file
    $baseUrl = "https://$S3_BUCKET.s3.amazonaws.com/$S3_PREFIX"
    $urlsFile = "$PSScriptRoot\s3-image-urls.txt"
    
    Write-Host "Generating image URLs file at $urlsFile"
    
    "# S3 Image URLs - Generated $(Get-Date)" | Out-File -FilePath $urlsFile
    "# Base URL: $baseUrl" | Out-File -FilePath $urlsFile -Append
    "# Format in config.js: s3.getImageUrl('filename.jpg')" | Out-File -FilePath $urlsFile -Append
    "" | Out-File -FilePath $urlsFile -Append
    
    Get-ChildItem -Path $LOCAL_IMAGE_PATH -File | ForEach-Object {
        "$baseUrl$($_.Name) - $($_.Name)" | Out-File -FilePath $urlsFile -Append
    }
    
    Write-Host "Done! Image URLs saved to $urlsFile"
}

Write-Host "Sync complete!"
