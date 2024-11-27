# DICOM to PDF Converter

## Overview

This Python application converts DICOM medical image files to PDF format and stores them in a PostgreSQL database. It provides an automated solution for converting medical imaging files with detailed logging and error handling.

## Features

- Converts multiple DICOM (.dcm) files to PDF
- Stores converted PDFs in a PostgreSQL database
- Supports configurable paths for download and PDF directories
- Provides detailed conversion logging
- Handles conversion errors gracefully

## Prerequisites

- Python 3.8+
- PostgreSQL
- DICOM conversion executable (configured in settings)
- Required Python packages:
  - `base64`
  - `logging`
  - `subprocess`
  - `os`
  - Custom modules: `convert_dcm2pdf.database.connect`, `convert_dcm2pdf.utils.exceptions`

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a configuration file with the following sections:

```ini
[dcm]
executable_path = /path/to/dicom/converter

[paths]
download_directory = ./downloads
pdf_directory = ./pdfs

[database]
host = localhost
port = 5432
database = your_database
user = your_username
password = your_password
```

## Usage

```python
from convert_dcm2pdf import DCMConverter
from your_config_manager import ConfigManager

# Initialize config manager
config_manager = ConfigManager('path/to/config.ini')

# Create converter instance
converter = DCMConverter(config_manager)

# Convert all DICOM files
converted_pdfs, error_files = converter.convert_all_dcm_files()
```

## Workflow

1. Place DICOM files in the configured download directory
2. Run `convert_all_dcm_files()`
3. Application will:
   - Detect DICOM files
   - Convert each file to PDF
   - Store PDFs in database
   - Log conversion progress and errors

## Output Details

When executed, the script will print:
- Total files found
- Each successfully converted file
- Summary of conversions (total processed, successful, failed)

## Error Handling

- Files that fail conversion are logged
- Conversion continues for remaining files
- Detailed error messages provided

## Database Schema

Ensure your PostgreSQL database has a table:
```sql
CREATE TABLE pdf_storage (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Logging

Utilizes Python's `logging` module for tracking conversion processes and errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

linkedin: https://www.linkedin.com/in/lucas-gabriel-de-paula-00007512a/
email: lucasgpaula7@gmail.com
