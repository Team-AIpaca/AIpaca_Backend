# Sign up API Specs
API to register for membership when membership information is entered.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `POST` | http://{address}:{port}/api/user/signup |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `email` | Yes | `String` | User's email address. If it's already registered, you can't use it duplicately. |
| `username` | Yes | `String` | User name. If it's already registered, you can't use it duplicately. |
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
    "email": "test@test.com",
    "username": "username",
    "password": "password"
}
```

## Response from API
### POST Response
```json
{
  "StatusCode": 201,
  "message": "User registered successfully.",
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
    "MissingFields": "email",
    "UnknownParams": "emails"
  }
}
```

### Missing IP Address or User Agent
Returns an error if there is no IP address or user agent value.

Example:
```json
{
  "StatusCode": 4003,
  "message": "Missing fields and Unknown parameters",
  "data": {
    "RequestTime": "2024-03-26T10:30:55.487194+00:00",
    "IPAddress": "Absent",
    "UserAgent": "Present"
  }
}
```

### Password requirements not met
Returns an error if the password conditions (at least 8 digits, alphabetical lowercase letters and numbers required) are not met.

Example:
```json
{
  "StatusCode": 400,
  "message": "Password must be at least 8 characters long and include both letters and numbers.",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00"
  }
}
```

### Duplicate email addresses or usernames
Returns an error if the email address or username is a duplicate.

Example:
```json
{
  "StatusCode": 400,
  "message": "Duplicate username or email.",
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