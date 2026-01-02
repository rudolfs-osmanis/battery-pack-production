# Battery Pack Production System

A desktop application for managing lithium battery pack production, built with **Python**, **Tkinter**, and **SQLite**.

The system supports cell parameter management, order registration with configurable layouts, automatic serial number generation, and CSV export for printing and production use.

---

## Features

### Cell Management
- Register battery cells with:
  - Manufacturer
  - Model number
  - Capacity (mAh)
  - Unit price (EUR)
- Add, edit, and delete cell records
- Data persisted in SQLite database

### Order Management
- Register production orders with:
  - Automatically generated order numbers
  - Client information
  - Pack quantity
  - Series / parallel configuration (S / P)
  - Selected cell model
  - Notes / configuration details
  - Status: `ACTIVE`, `DISCONTINUED`, `FINISHED`
- Automatic calculation of:
  - Pack capacity
  - Total cell cost
  - Nominal voltage (S × 3.7 V)

### Serial Number Generation
- Select ACTIVE orders
- Generate serial numbers in format: {S}S{P}P{capacity}-{order_no}-{sequence} (e.g. 6S3P15000-ORD-0002-003)
- Export serial data to CSV (`;` separated) with columns:
- Serial number
- Capacity (mAh)
- Voltage (V)

---

## Technology Stack
- **Python 3**
- **Tkinter** – GUI
- **SQLite** – local database
- **CSV** – data export

---

## Project Structure

```text
Bateriju_pakas/
├── app.py
├── README.md
├── .gitignore
├── db/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.py
│   ├── cell_repo.py
│   └── order_repo.py
└── ui/
    ├── __init__.py
    ├── main_window.py
    ├── cells_window.py
    ├── orders_window.py
    └── serials_window.py
```
---

## Installation & Running

### Requirements
- Python 3.x
- No external dependencies required

### Run the application

python app.py

On first run:

SQLite database is created automatically

Tables are initialized if they do not exist

### Database

Uses SQLite (.sqlite3)
Stored locally
Database files are not tracked in Git
Foreign key constraints enabled
WAL journal mode enabled for reliability

### Notes

This application is designed for local desktop use
No internet connection required
No sensitive personal data stored
Suitable for small-scale production environments or educational projects

### License

MIT License
You are free to use, modify, and distribute this project.

### Author


Rudolfs Osmanis


