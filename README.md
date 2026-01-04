# AEE Bot - Acta de Evidencia Electrónica

<div align="center">

![AEE Bot Logo](https://img.shields.io/badge/AEE%20Bot-v3.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Telegram](https://img.shields.io/badge/Telegram%20Bot-API-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Enterprise-Grade Digital Preservation System for Telegram**

[![Stars](https://img.shields.io/github/stars/aee-bot/aee-protocol.svg?style=social&label=Star)](https://github.com/aee-bot/aee-protocol)
[![Forks](https://img.shields.io/github/forks/aee-bot/aee-protocol.svg?style=social&label=Fork)](https://github.com/aee-bot/aee-protocol)
[![Issues](https://img.shields.io/github/issues/aee-bot/aee-protocol.svg)](https://github.com/aee-bot/aee-protocol/issues)

</div>

## Overview

AEE Bot is a professional digital preservation system that provides cryptographic certification of file integrity through Telegram. It combines SHA-256 hashing, SQLite persistence, and professional PDF certificate generation to create a complete forensic evidence solution.

### Key Features

- **Cryptographic Integrity**: SHA-256 hashing (NIST FIPS 180-4 compliant)
- **Professional Certificates**: PDF-based forensic evidence certificates
- **Enterprise Database**: SQLite with optimized indexing
- **Telegram Integration**: Inline buttons for seamless user experience
- **User History**: Complete preservation tracking with `/historial`
- **Signature Ready**: Reserved fields for digital signatures
- **Forensic Logging**: Complete audit trail with DEBUG-level logging

## Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

```bash
# Clone the repository
git clone https://github.com/aee-bot/aee-protocol.git
cd aee-protocol

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token

# Start the bot
python main.py
```

### Basic Usage

1. **Start the bot**: Send `/start` to your bot
2. **Preserve a file**: Send any photo or document
3. **Get certificate**: Press the "Descargar Certificado PDF" button
4. **Verify integrity**: Use `/verificar` to compare files
5. **View history**: Send `/historial` to see your preservations

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome message and capabilities | `/start` |
| `/verificar` | Compare file integrity with previous hash | Reply to hash message with `/verificar` + new file |
| `/historial` | Show your last 5 preservations | `/historial` |

## Architecture

```
├── main.py                 # Entry point with database initialization
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── SPECIFICATION.md       # Technical specification
├── ROADMAP.md            # Development roadmap
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── .gitignore           # Git ignore patterns
├── inspect_database.py   # Database inspection utility
└── aee/
    ├── __init__.py        # Module exports
    ├── database.py        # SQLite persistence layer
    ├── certificate.py     # PDF certificate generation
    └── telegram_bot.py    # Main bot logic with handlers
```

## Technical Details

### Database Schema

```sql
CREATE TABLE preservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash VARCHAR(64) UNIQUE NOT NULL,      -- SHA-256 hash
    file_name VARCHAR(255),                      -- Original filename
    mime_type VARCHAR(100),                      -- MIME type
    file_size INTEGER NOT NULL,                  -- File size in bytes
    user_id VARCHAR(20) NOT NULL,                -- Telegram user ID
    timestamp_utc DATETIME NOT NULL,              -- UTC timestamp
    _signature TEXT                            --  signature (reserved)
);

-- Performance indexes
CREATE INDEX ix_preservations_file_hash ON preservations(file_hash);
CREATE INDEX ix_preservations_user_id ON preservations(user_id);
```

### Certificate Content

Each PDF certificate includes:
- **Header**: "CERTIFICADO DE PRESERVACIÓN DIGITAL"
- **Preservation Info**: ID, timestamp, user details
- **Cryptographic Integrity**: SHA-256 hash (highlighted)
- **File Properties**: Name, MIME type, size
- **Legal Disclaimer**: Scope and limitations
- **Technical Specs**: NIST compliance information
- ** Field**: Reserved for future signatures
- **Footer**: Generation timestamp and system info

### Security Features

- **Hash Uniqueness**: Database constraint prevents duplicates
- **User Validation**: Only owners can download their certificates
- **Timestamp Integrity**: UTC timestamps with RFC 3339 format
- **Audit Trail**: Complete logging of all operations
- **Legal Clarity**: Clear scope of certification

## Usage Statistics

Monitor your system with the built-in database inspector:

```bash
python inspect_database.py
```

This shows:
- Database file size and structure
- Total preservations and users
- Individual preservation records
- Integrity verification results
- Index optimization status

## Database Inspection

The `inspect_database.py` utility provides comprehensive database analysis:

```bash
$ python inspect_database.py

================================================================================
INSPECTOR DE BASE DE DATOS - AEE Bot v3.0
================================================================================

Archivo: aee_preservations.db
Tamano: 16384 bytes (16.00 KB)

--------------------------------------------------------------------------------
📋 ESQUEMA DE TABLAS
--------------------------------------------------------------------------------

Tabla: preservations

  Columnas:
    • id: INTEGER NOT NULL [PRIMARY KEY]
    • file_hash: VARCHAR(64) NOT NULL
    • file_name: VARCHAR(255) NULL
    • mime_type: VARCHAR(100) NULL
    • file_size: INTEGER NOT NULL
    • user_id: VARCHAR(20) NOT NULL
    • timestamp_utc: DATETIME NOT NULL
    • _signature: TEXT NULL

--------------------------------------------------------------------------------
ESTADÍSTICAS
--------------------------------------------------------------------------------

  Total de registros: 2
  Tamaño total de archivos: 38 bytes (0.00 MB)
  Usuarios únicos: 1
```

## Environment Configuration

Create a `.env` file with your configuration:

```bash
# Telegram Bot Token (required)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=DEBUG

# Database Path
DATABASE_PATH=aee_preservations.db

# Certificates Directory
CERTIFICATES_DIR=./certificates/
```

## Dependencies

| Package | Version | Purpose |
|---------|--------|---------|
| `python-telegram-bot` | 20.7 | Telegram Bot API |
| `SQLAlchemy` | 2.0.23 | Database ORM |
| `reportlab` | 4.0.7 | PDF Generation |
| `python-dotenv` | 1.0.0 | Environment Management |
| `asyncio` | 3.4.3 | Async Support |
| `pydantic` | 2.5.0 | Data Validation |

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
```

### Systemd Service

```ini
[Unit]
Description=AEE Bot Service
After=network.target

[Service]
Type=simple
User=aee
WorkingDirectory=/opt/aee-bot
Environment=PYTHONPATH=/opt/aee-bot
ExecStart=/usr/bin/python3 /opt/aee-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Security Considerations

### What is Certified
- **Binary Integrity**: SHA-256 hash of the exact file bytes
- **Timestamp**: UTC time of preservation
- **User Identity**: Telegram user who performed preservation
- **File Metadata**: Size, name, and MIME type

### What is NOT Certified
- **Content Veracity**: Truthfulness or accuracy of information
- **Legal Compliance**: Whether content follows laws or regulations
- **Authorship**: Who created or owns the content
- **Context**: Appropriateness or meaning of the content

### Best Practices
- Keep your bot token secure
- Regular backup of the SQLite database
- Monitor logs for unusual activity
- Validate certificates independently when needed

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/aee-protocol.git
cd aee-protocol

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest

# Start development server
python main.py
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans:

- **v3.1**: Digital Signature Integration
- **v3.2**: Blockchain Integration (Merkle Trees, Smart Contracts)
- **v3.3**: Analytics Dashboard (Web Interface, Reporting)
- **v3.4**: Multi-Platform Support (Discord, Slack, WhatsApp)
- **v3.5**: Enterprise Features (LDAP, SIEM, Compliance)

## Troubleshooting

### Common Issues

**Bot doesn't start**
```bash
# Check your bot token
echo $TELEGRAM_BOT_TOKEN

# Verify Telegram API access
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

**Database errors**
```bash
# Inspect database
python inspect_database.py

# Reset database (WARNING: destructive)
rm aee_preservations.db
python main.py
```

**Certificate generation fails**
```bash
# Check ReportLab installation
python -c "from reportlab.pdfgen import canvas; print('OK')"

# Verify certificates directory
ls -la ./certificates/
```

### Getting Help

1. Check the [Issues](https://github.com/aee-bot/aee-protocol/issues) page
2. Search existing discussions
3. Create a new issue with detailed information
4. Join our community Discord (link in repository)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) for the excellent Telegram framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for powerful database ORM
- [ReportLab](https://www.reportlab.com/) for PDF generation capabilities
- [NIST](https://www.nist.gov/) for SHA-256 and cryptographic standards

## Support

- Issues: [GitHub Issues](https://github.com/aee-bot/aee-protocol/issues)


---

<div align="center">

**[Star this repo](https://github.com/aee-bot/aee-protocol) if it helped you!**

Made with dedication by the AEE Team

</div>
