import os
import sys

# Attempt to set up logging as the VERY FIRST operation
LOG_FILE_PATH = '' # Initialize
try:
    # Determine script directory for logging
    # Note: __file__ might not be defined if script is run in certain embedded ways, but usually is.
    script_dir_for_log = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    LOG_FILE_PATH = os.path.join(script_dir_for_log, 'debug_sync_s3.log')
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as lf:
        lf.write("--- Log Start (sync_s3.py) ---\n")
        lf.write(f"Initial log path: {LOG_FILE_PATH}\n")
except Exception as e:
    # If logging setup itself fails, print to stderr as a last resort
    print(f"CRITICAL: Failed to initialize logging for sync_s3.py: {e}", file=sys.stderr)
    # We might not have LOG_FILE_PATH correctly set here, so can't log to file.

# Now, define the log_message function that uses LOG_FILE_PATH
def log_message(message, level='INFO'):
    formatted_message = f"{level}: {message}\n"
    # Also print to original stdout/stderr for good measure
    if level == 'ERROR':
        print(formatted_message.strip(), file=sys.stderr)
    else:
        print(formatted_message.strip(), file=sys.stdout)
    
    if LOG_FILE_PATH: # Only attempt to log to file if path was set
        try:
            with open(LOG_FILE_PATH, 'a', encoding='utf-8') as lf:
                lf.write(formatted_message)
        except Exception as e:
            print(f"ERROR: Failed to write to log file {LOG_FILE_PATH}: {e}", file=sys.stderr)

# Proceed with other imports AFTER basic logging is attempted
import subprocess # To run AWS CLI
log_message("Successfully imported subprocess.", level='DEBUG')

ABS_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

log_message(f"DEBUG: __file__ = {__file__}", level='DEBUG')
log_message(f"DEBUG: ABS_SCRIPT_DIR = {ABS_SCRIPT_DIR}", level='DEBUG')

log_message(f"DEBUG: __file__ = {__file__}", level='DEBUG')
log_message(f"DEBUG: ABS_SCRIPT_DIR = {ABS_SCRIPT_DIR}", level='DEBUG')

# Configuration
LOCAL_IMAGE_BASE_PATH = os.path.join(ABS_SCRIPT_DIR, 'docs', 'images')
log_message(f"DEBUG: LOCAL_IMAGE_BASE_PATH = {LOCAL_IMAGE_BASE_PATH}", level='DEBUG')
S3_BUCKET_NAME = "photos-joyfulphotographs-com"
S3_PREFIX = "website-images/"
AWS_PROFILE_NAME = "joyful-photos"

def print_error(message):
    log_message(message, level='ERROR')

def print_success(message):
    log_message(message, level='SUCCESS')

def print_info(message):
    log_message(message, level='INFO')

def main():
    print_info("Starting S3 sync process...")
    log_message(f"Local image source: {LOCAL_IMAGE_BASE_PATH}", level='DEBUG')
    log_message(f"S3 Bucket: {S3_BUCKET_NAME}", level='DEBUG')
    log_message(f"S3 Prefix: {S3_PREFIX}", level='DEBUG')
    log_message(f"AWS Profile: {AWS_PROFILE_NAME}", level='DEBUG')

    if not os.path.isdir(LOCAL_IMAGE_BASE_PATH):
        log_message(f"Local image directory not found: {LOCAL_IMAGE_BASE_PATH}", level='ERROR')
        sys.exit(1)

    s3_target_uri = f"s3://{S3_BUCKET_NAME}/{S3_PREFIX}"
    local_source_path = os.path.join(LOCAL_IMAGE_BASE_PATH, '') 

    aws_command = [
        "aws", "s3", "sync",
        local_source_path,
        s3_target_uri,
        "--profile", AWS_PROFILE_NAME,
    ]

    log_message(f"Executing AWS CLI command: {' '.join(aws_command)}", level='INFO')

    try:
        process = subprocess.run(aws_command, capture_output=True, text=True, check=False, shell=False)
        
        if process.stdout:
            log_message("AWS CLI stdout:", level='INFO')
            for line in process.stdout.splitlines():
                log_message(line, level='INFO') # Log each line of stdout
        
        if process.stderr:
            log_message("AWS CLI stderr:", level='WARNING')
            for line in process.stderr.splitlines():
                log_message(line, level='WARNING') # Log each line of stderr

        if process.returncode == 0:
            log_message("AWS S3 sync completed successfully.", level='SUCCESS')
            print_success("S3 sync completed successfully.")
            sys.exit(0)
        elif process.returncode == 2:
            log_message("AWS S3 sync completed, but some files may not have been transferred (exit code 2). Review logs.", level='WARNING')
            print_warning("S3 sync completed, but some files may not have been transferred. Check debug_sync_s3.log")
            sys.exit(0) # Still treat as success for the hook
        else:
            log_message(f"AWS S3 sync failed with exit code {process.returncode}. Error: {process.stderr}", level='ERROR')
            print_error(f"S3 sync failed. Check debug_sync_s3.log")
            sys.exit(1)
            
    except FileNotFoundError:
        log_message("Error: 'aws' command not found. Please ensure AWS CLI is installed and in your PATH.", level='ERROR')
        print_error("'aws' command not found. Ensure AWS CLI is installed and in PATH.")
        sys.exit(1)
    except Exception as e:
        log_message(f"An unexpected error occurred while running AWS CLI sync: {e}", level='ERROR')
        print_error(f"An unexpected error occurred during S3 sync. Check debug_sync_s3.log")
        sys.exit(1)

if __name__ == "__main__":
    log_message("This script uses AWS CLI. Ensure it's installed and configured ('aws configure --profile joyful-photos').", level='INFO')
    main()
