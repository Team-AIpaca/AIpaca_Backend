# Login API Specs
API that verifies login information and returns a result when you enter it.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `POST` | http://{address}:{port}/api/trans/papago |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `username` | Yes | `String` | User name. |
| `password` | Yes | `String` | The user's password, which must be at least 8 characters long and contain alphabetical lowercase letters and numbers. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Translation successful` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |

# Example
## Request to API
### POST Request
```json
{
    "username": "username",
    "password": "password"
}
```

## Response from API
### POST Response
```json
{
  "StatusCode": 200,
  "message": "User authenticated successfully.",
  "data": {
    "RequestTime": "2024-03-26T10:22:19.032571+00:00",
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
    "MissingFields": "password",
    "UnknownParams": "passwords"
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

### Other errors
Other errors are output with an error message.

Example:
```json
{
  "StatusCode": 500,
  "message": "Database error: error",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00",
  }
}
```