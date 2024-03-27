# Return User's achievements list API Specs
API that allows a particular user to complete a challenge through API if they meet the challenge conditions.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `POST` | http://{address}:{port}/api/challenge/achieve |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `username` | Yes | `String` | Name of the user who wants to register the challenge |
| `password` | Yes | `String` | Password for `user` |
| `achievement_id` | Yes | `String` | Challenge id |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Achievement recorded successfully.` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |

# Example
## Request to API
### POST Request
```json
{
    "username": "username",
    "password": "password",
    "achievement_id": "acv003"
}
```

## Response from API
### POST Response
```json
{
  "StatusCode": 200,
  "message": "Achievement recorded successfully.",
  "data": {
    "RequestTime": "2024-03-27T09:56:32.719497+00:00"
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
    "MissingFields": "achievement_id",
    "UnknownParams": "achievement_ids"
  }
}
```
### Missing achievement list JSON file
If the `json` file containing the achievement list (`list.json`) is missing, an error will be thrown.

Example:
```json
{
  "StatusCode": 400,
  "message": "Achievement list file not found.",
  "data": {
    "RequestTime": "2024-03-27T06:11:05.465222+00:00"
  }
}
```

### Entering an achievement ID that doesn't exist
Returns an error if you enter an achievement ID that doesn't exist in `list.json`.

Example:
```json
{
  "StatusCode": 400,
  "message": "Achievement ID does not exist.",
  "data": {
    "RequestTime": "2024-03-27T10:03:09.070387+00:00"
  }
}
```

### Attempting to redeem an already redeemed achievement
Returns an error if you try to redeem an achievement that has already been redeemed.

Example:
```json
{
  "StatusCode": 409,
  "message": "Duplicate achievement record.",
  "data": {
    "RequestTime": "2024-03-27T10:04:46.546831+00:00",
    "duplicate": "acv003",
    "achievement_date": "2024-03-27T18:56:32"
  }
}
```

### Unknown Server Error
If an unknown error occurs while checking the language value, the error message `Unknown Server Error` is displayed.

Example:
```json
{
  "StatusCode": 5009,
  "message": "Unknown Server Error",
  "data": {
    "RequestTime": "2024-03-26T12:36:32.755601+00:00"
  }
}
```

### Problems with login
For login-related issues, such as mismatched membership information, see [login README.md](../../user/login/README.md)!