# Tec 40-45 Gas Planning Sheet

A **CustomTkinter-based desktop application** for scuba gas planning.  
This tool helps divers and instructors quickly calculate and document gas requirements, rock bottom reserves, decompression stops, and emergency reserves for **Tec 40–45 level dives**.  

The app supports saving/loading plans as JSON, exporting to PDF for record-keeping, and includes built-in calculation logic for ATA, SAC, gas volumes, and reserve estimates.

---

## ✨ Features

- **Interactive UI** built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Automatic calculations**:
  - ATA from depth  
  - SAC × ATA × time → Gas Volume  
  - Gas reserve updates for two divers  
  - Midpoint depth interpolation  
  - Deco gas totals
- **Sections included**:
  - General Info (depth, mix, bottom time, gradient factors)  
  - Gas Reserve / Rock Bottom  
  - Gas Reserve (Emergency) with 3-row calculations  
  - Bottom Gas Requirements  
  - Deco Stops (6 standard stops)  
  - Deco Gas Requirements (linked with Deco Stops)  
- **Data persistence**:
  - Save plans to `.json`  
  - Load previous plans  
  - Export full plan to **PDF** (formatted tables with ReportLab)  
- **Utility buttons**: Save, Load, Clear All, Export to PDF

---

## 📦 Installation

Download and Run .EXE found in releases
