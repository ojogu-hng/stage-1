# **Intelligent String Property Analyzer API** ✨

Unleash the power of text with the Intelligent String Property Analyzer API! This FastAPI service provides robust, asynchronous tools for comprehensive string analysis, from basic properties like length and palindrome detection to advanced features like SHA-256 hashing and natural language query filtering. Seamlessly integrate powerful text processing into your applications.

## Overview
This project implements a RESTful API using Python with FastAPI for analyzing and managing string data. It leverages SQLAlchemy with an asynchronous driver (asyncpg) for database interactions, Pydantic for data validation and serialization, and Uvicorn for the ASGI server. The system automatically computes various properties for ingested strings, stores them, and allows for flexible retrieval and filtering, including interpreting natural language queries.

## Features
- **String Property Computation**: Automatically calculates length, palindrome status, unique character count, word count, SHA-256 hash, and character frequency map for every stored string.
- **CRUD Operations**: Supports creating, retrieving (individually or filtered), and deleting string entries.
- **Natural Language Query Filtering**: Allows clients to filter stored strings using human-readable queries (e.g., "all single word palindromic strings").
- **Asynchronous Database Access**: Utilizes SQLAlchemy's async capabilities with `asyncpg` for efficient, non-blocking database operations.
- **Robust Error Handling**: Implements custom exception handlers for common API errors (e.g., 404 Not Found, 409 Conflict) and Pydantic/FastAPI validation errors.
- **Structured Logging**: Integrates `rich` for enhanced console logging and provides file-based logging for exceptions and operational events.
- **CORS Support**: Configured to handle Cross-Origin Resource Sharing for flexible client-side integration.

## Getting Started
### Installation 🚀
To get a copy of the project up and running on your local machine, follow these steps.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/ojogu-hng/stage-1.git
    cd stage-1
    ```

2.  **Create and Activate a Virtual Environment**:
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    Install the required Python packages using `pip`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**:
    Start the FastAPI application using Uvicorn.
    ```bash
    uvicorn src.main:app --reload
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

### Environment Variables
The application requires the following environment variable to connect to the database. Create a `.env` file in the root directory (where `requirements.txt` is located) and populate it with the following:

-   **`DATABASE_URL`**: The connection string for your PostgreSQL database.
    ```
    DATABASE_URL="postgresql+asyncpg://user:password@host:port/database_name"
    ```
    Example for a local PostgreSQL instance:
    ```
    DATABASE_URL="postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/string_analyzer_db"
    ```

## API Documentation
### Base URL
The API is served from the root path. Assuming a local development setup, the base URL is: `http://127.0.0.1:8000`

### Endpoints

#### `POST /strings`
Creates a new string entry, analyzes its properties, and stores it in the database.

**Request**:
```json
{
  "value": "string to analyze"
}
```

**Response**:
```json
{
  "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "value": "hello",
  "properties": {
    "length": 5,
    "is_palindrome": false,
    "unique_characters": 4,
    "word_count": 1,
    "sha256_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    "character_frequency_map": {
      "h": 1,
      "e": 1,
      "l": 2,
      "o": 1
    }
  },
  "created_at": "2023-10-27T10:00:00.000000+00:00"
}
```

**Errors**:
- `409 Conflict`: If the string value already exists in the database.
  ```json
  {
    "detail": "'hello' already exists"
  }
  ```
- `422 Unprocessable Entity`: If the request payload is invalid.

#### `GET /strings/filter-by-natural-language`
Filters stored strings based on a natural language query.

**Request**:
Query Parameters:
- `query` (string, **required**): The natural language query for filtering (e.g., "all single word palindromic strings", "strings longer than 10 characters", "strings containing the letter z").

**Response**:
```json
{
  "data": [
    {
      "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "value": "level",
      "properties": {
        "length": 5,
        "is_palindrome": true,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "3e9b14b18429b68194a3e7e231b48b111b7147779c4a037b420f1a6f87a8f15d",
        "character_frequency_map": {
          "l": 2,
          "e": 2,
          "v": 1
        }
      },
      "created_at": "2023-10-27T10:05:00.000000+00:00"
    }
  ],
  "count": 1,
  "interpreted_query": {
    "original": "single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true,
      "min_length": null,
      "max_length": null,
      "contains_character": null
    }
  }
}
```

**Errors**:
- `422 Unprocessable Entity`: If the `query` parameter is missing or invalid.

#### `GET /strings/{string_value}`
Retrieves a specific string entry and its properties by its value.

**Request**:
Path Parameters:
- `string_value` (string, **required**): The exact string value to retrieve.

**Response**:
```json
{
  "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "value": "world",
  "properties": {
    "length": 5,
    "is_palindrome": false,
    "unique_characters": 5,
    "word_count": 1,
    "sha256_hash": "7488219c6f2e86a51240c1e84a28905b796696d744b1c55470d0551068205562",
    "character_frequency_map": {
      "w": 1,
      "o": 1,
      "r": 1,
      "l": 1,
      "d": 1
    }
  },
  "created_at": "2023-10-27T10:10:00.000000+00:00"
}
```

**Errors**:
- `404 Not Found`: If no string with the given `string_value` is found.
  ```json
  {
    "detail": "String 'nonexistent' not found or does not match criteria."
  }
  ```

#### `GET /strings`
Retrieves all stored strings with optional filtering capabilities.

**Request**:
Query Parameters (all optional):
- `is_palindrome` (boolean): Filters for strings that are palindromes (`true`) or not (`false`).
- `min_length` (integer): Filters for strings with a length greater than or equal to this value.
- `max_length` (integer): Filters for strings with a length less than or equal to this value.
- `word_count` (integer): Filters for strings with an exact word count.
- `contains_character` (string): Filters for strings containing the specified character (case-insensitive).

**Response**:
```json
{
  "data": [
    {
      "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "value": "apple",
      "properties": {
        "length": 5,
        "is_palindrome": false,
        "unique_characters": 4,
        "word_count": 1,
        "sha256_hash": "3a7bd3e2360a3d29ee15e197b14022a4563df4e2c9e7792a7e719c8f0d575005",
        "character_frequency_map": {
          "a": 1,
          "p": 2,
          "l": 1,
          "e": 1
        }
      },
      "created_at": "2023-10-27T10:15:00.000000+00:00"
    },
    {
      "id": "c1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
      "value": "banana",
      "properties": {
        "length": 6,
        "is_palindrome": false,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "24cb140f7b0b2e8c2a3828945a05b22b11568c17b889d3119047b36f73448a31",
        "character_frequency_map": {
          "b": 1,
          "a": 3,
          "n": 2
        }
      },
      "created_at": "2023-10-27T10:20:00.000000+00:00"
    }
  ],
  "count": 2,
  "filters_applied": {
    "is_palindrome": null,
    "min_length": null,
    "max_length": null,
    "word_count": null,
    "contains_character": null
  }
}
```

**Errors**:
- `422 Unprocessable Entity`: If any query parameter has an invalid type or format.

#### `DELETE /strings/{string_value}`
Deletes a specific string entry from the database.

**Request**:
Path Parameters:
- `string_value` (string, **required**): The exact string value to delete.

**Response**:
```json
{
  "message": "String 'delete_me' deleted successfully."
}
```

**Errors**:
- `404 Not Found`: If no string with the given `string_value` is found.
  ```json
  {
    "detail": "String 'nonexistent_to_delete' not found."
  }
  ```

## Technologies Used
| Technology         | Description                                     | Link                                                        |
| :----------------- | :---------------------------------------------- | :---------------------------------------------------------- |
| **Python**         | Programming language for the backend            | [python.org](https://www.python.org/)                       |
| **FastAPI**        | High-performance web framework for building APIs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)       |
| **SQLAlchemy**     | SQL toolkit and Object-Relational Mapper (ORM)  | [sqlalchemy.org](https://www.sqlalchemy.org/)               |
| **AsyncPG**        | Asynchronous PostgreSQL driver                  | [asyncpg.org](https://www.asyncpg.org/)                     |
| **Pydantic**       | Data validation and settings management         | [pydantic.dev](https://pydantic.dev/)                       |
| **Uvicorn**        | ASGI server for running FastAPI applications    | [www.uvicorn.org](https://www.uvicorn.org/)                 |
| **Rich**           | Library for rich text and beautiful formatting in the terminal | [rich.readthedocs.io](https://rich.readthedocs.io/en/stable/) |

## Contributing 🤝
We welcome contributions to enhance the Intelligent String Property Analyzer API! If you have suggestions for improvements, new features, or bug fixes, please follow these guidelines:

1.  **Fork the Repository**: Start by forking the project to your GitHub account.
2.  **Create a New Branch**: Create a branch for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/issue-description`.
3.  **Make Your Changes**: Implement your changes and ensure they adhere to the project's coding style.
4.  **Write Tests**: Add appropriate tests for your changes to maintain robust functionality.
5.  **Commit Your Changes**: Write clear and concise commit messages.
6.  **Push to Your Fork**: Push your branch to your forked repository.
7.  **Open a Pull Request**: Submit a pull request to the `main` branch of the original repository, describing your changes and their benefits.

## Author Info
- **Your Name**: [Your LinkedIn Profile](https://linkedin.com/in/your-username) | [Your Twitter Profile](https://twitter.com/your-username)

---
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-blue?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.30.0-purple?logo=uvicorn)](https://www.uvicorn.org/)

[![Readme was generated by Dokugen](https://img.shields.io/badge/Readme%20was%20generated%20by-Dokugen-brightgreen)](https://www.npmjs.com/package/dokugen)