# IES-Tools

A comprehensive Python-based toolkit for automating project creation and management for the Data Models class in smartgrids.

## Overview

IES-Tools is designed to streamline the process of creating working projects tailored for smartgrid data modeling based on provided specifications. The tool serves two main functions:

1. **Code Generation** - Automatically generate code for various components based on specifications
2. **Data Management** - Act as a Content Management System with CRUD operations for existing project specifications

## Features

### Code Generator

- Generate model definitions for smartgrid components
- Create enumeration types
- Generate XML data for testing
- Produce converter methods for data transformation
- Create importer methods for data import
- Generate server classes for backend implementation
- Generate server enum classes

### Data Manager

- View existing project specifications
- Filter specifications based on criteria
- Create new project specifications
- Copy existing specifications to new locations
- Delete project specifications

## Installation

1. Clone the repository:

```bash

git clone https://github.com/CoekCx/IES-Tools

cd IES-Tools

```

2. Install the required dependencies:

```bash

pip install -r requirements.txt

```

## Usage

Run the main application:

```bash

python main.py

```

### Main Menu

The main menu offers two primary options:

- **Code Generator** - Access code generation features
- **Data Manager** - Access specification management features

### Code Generator

1. **Set Project Specification** - Define or load a project specification
2. **Generate Model Defines** - Create model definitions for your project
3. **Generate Enums** - Create enumeration types
4. **Generate XML data** - Generate test data in XML format
5. **Generate Converter Methods** - Create methods to convert between formats
6. **Generate Importer Methods** - Create methods to import data
7. **Generate Server Classes** - Create server-side class implementations
8. **Generate Server Enum Classes** - Create server-side enumeration implementations

### Data Manager

1. **View Project Specifications** - List all available specifications
2. **Filter Project Specifications** - Find specifications matching certain criteria
3. **Create Project Specification** - Create a new specification
4. **Copy Project Specification** - Copy an existing specification
5. **Delete Project Specification** - Remove a specification

## Project Structure

- **code_generator/** - Contains the code generation functionality
- **data_manager/** - Contains the specification management system
- **common/** - Shared models, utilities, and constants
- **data_reader/** - Tools for reading specifications
- **prompter/** - User interface components for data input

## Dependencies

- inquirer2 - For interactive command-line interfaces
- tabulate - For formatted table output
- termcolor - For colored terminal output
- colorama - For cross-platform colored terminal text
- PIL - For image processing
- pyperclip - For clipboard operations
- tqdm - For progress bar display

## License

This project is licensed under the MIT License - see the LICENSE file for details.
