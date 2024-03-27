# Server connect check API Specs
API that verify that the server is properly connected and processing requests.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/ping |

## Request Header
| Header Name | Notes |
|-------------|-------|
| None | No required request header! |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| None | None | None | Does not require a value when requesting version information. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Successful version information request` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/ping
```

### POST Request
```url
http://{address}:{port}/ping
```

## Response from API
### GET Response
```json
{
  "StatusCode": 200,
  "message": "GET request processed. Hello, world!",
  "data": {
    "RequestTime": "2024-03-26T05:38:15.713822+00:00"
  }
}
```

### POST Response
```json
{
  "StatusCode": 200,
  "message": "POST request processed. Hello, world!",
  "data": {
    "RequestTime": "2024-03-26T05:38:15.713822+00:00"
  }
}
```

## Error Response
The Version API is not error-prone, so if you get an error, it's probably coming from somewhere else.