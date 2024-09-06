# Pilot Log Management System
## Overview

The Pilot Log Management System is a Django 5.1 project designed to manage and manipulate pilot log data. The system includes modules for importing data from JSON files, storing the data in a normalized database schema, and exporting the data into a CSV format. The project is structured to be reusable, maintainable, and adaptable to future changes.

### Features

- Data Importer: A reusable module for importing pilot log data from JSON files.
- Django App: A pilotlog Django app with data models designed to efficiently store and manage pilot log data.
- CSV Exporter: A reusable module for exporting pilot log data to a CSV file following a specified template.

## Project Structure

The main file in this project is the [import_export.py](apps/pilotlog/helpers/import_export.py)  module.
The module is responsible for importing and exporting data from and to the database, based on the ForeFlight Logbook format.

In the folder [Data](Data), you will find the JSON files that will be imported and the CSV file that will be exported.

To se more details about the requirements, please refer to the [Apexive django project](https://us.apexive.com/coding-test-assignments).

### Project Overview
This project provides a reusable solution for importing and exporting data to and from the database in a Django application, based on the **ForeFlight Logbook** format. 
The code is structured to allow reusability across different implementations for importing JSON files and exporting CSV files.

Considering the requirements:

    - Reusability: Both the importer and exporter should be implemented as reusable modules.

    - Data Model Design: The data model must adhere to DRY (Don't Repeat Yourself) principles and follow a normalized SQL ORM schema. Design with future adaptability in mind, avoiding hardcoding of names or rigid structures.

    - Future Changes Consideration: Anticipate potential changes in the models and structure your code to accommodate such evolutions with minimal disruption.


To address the requirements of reusability, data model design, and future adaptability while managing complexity, I opted for a flexible yet straightforward solution with the DynamicTable model. 

By leveraging a single DynamicTable model with a JSONField to store diverse and evolving attributes in the meta field, I balance the need for flexibility with minimal schema complexity. 

This approach allows for handling various data structures without frequent migrations, accommodating future changes more gracefully. Although this solution sacrifices some level of normalization and query performance compared to a more rigid schema, it simplifies maintenance and adapts well to evolving data needs. 

This choice reflects a pragmatic approach to managing data complexity, aligning with the goal of creating a maintainable and adaptable system.

---

### Prerequisites
- Python 3.10+
- Django 5.1+
- PostgreSQL 14+
- Install necessary packages from `requirements.txt`

Using django-bulk-load library for bulk loading data into the database.

---

### Configure the env variables for the project

```bash
  export DB_NAME=apexive && export DB_USER=apexive && export DB_PASSWORD='dbpass' && export DB_HOST=ip_db && export SECRET_KEY="secretpassrnd"
```


### Import/Export Feature

The **import_export.py** module provides flexible and reusable functions for importing JSON data into the database and exporting the data in a structured CSV format. This module can be abstracted for other logbook or data import/export scenarios.

#### Import Data
To import data from a JSON file into the database, run the following command:

```bash
python3 manage.py import file_name.json
```

#### Export Data
To export the data to a CSV file, use the following command:

```bash
python3 manage.py export file_name.csv
```

---

### Abstract Design
The **pilotlog/helpers/import_export.py** file is designed to be abstract and reusable for other types of data beyond ForeFlight. You can extend or modify the import/export logic and mappings by customizing the functions in the module or using different mappings in `mappings.py`.

Feel free to adapt the import and export commands for your specific data models or formats.