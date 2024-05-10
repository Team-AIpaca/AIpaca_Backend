# Backup data API Specs
API to backup locally stored db files (.db).

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `POST` | http://{address}:{port}/api/data/backup |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `username` | Yes | `String` | User name. |
| `password` | Yes | `String` | The user's password, which must be at least 8 characters long and contain alphabetical lowercase letters and numbers. |
| `sql_file` | Yes | `application/x-sqlite3` | DB file with all information, including evaluation results. |
| `sql_hash` | Yes | `String` | `sql_file`'s SHA-256 hash value. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return message on successful or failure request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |

# Example
## Request to API
### POST Request
```json
{
    "username": "username",
    "password": "password",
    "sql_file": "{db file name}",
    "sql_hash": "aw4qasfqqaasfda"
}
```

## Response from API
### POST Response
```json
{
  "StatusCode": 200,
  "message": "Backup successful.",
  "data": {
    "RequestTime": "2024-03-26T10:22:19.032571+00:00"
  }
}
```

## Error Response
### GET Request
If a GET request is sent, an error message is output.

```json
{
    "StatusCode": 4001,
    "message": "Cannot process GET request. Please use POST method.",
    "data": {
        "RequestTime": "2024-03-26T10:30:55.487194+00:00"
    }
}
```

### Required field not filled in / Unknown field filled in
Missing required fields are listed in MissingFields, and unknown fields are listed in UnknownParams.

Example:
```json
{
  "StatusCode": 4003,
  "message": "Missing fields and Unknown parameters",
  "data": {
    "RequestTime": "2024-03-26T10:30:55.487194+00:00",
    "MissingFields": "sql_hash",
    "UnknownParams": "sql_hashs"
  }
}
```

### User information not found
Returns an error when user information is not found.

Example:
```json
{
  "StatusCode": 401,
  "message": "User does not exist.",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00"
  }
}
```

### Password mismatch
Returns an error if the passwords don't match.

Example:
```json
{
  "StatusCode": 401,
  "message": "Duplicate entry found",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00"
  }
}
```

### Hash mismatch
Returns an error if the hash value don't match.

Example:
```json
{
  "StatusCode": 401,
  "message": "File hash does not match.",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00"
  }
}
```