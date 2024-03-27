# Version API Specs
The Version API returns the version of the service. The service version information is taken from the `.env` file `SERVICE_VERSION` value. Check the [env_README.md](../../env_README.md) file for more information!

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/version |

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
| `Version` | `Int` or `String`(Depends on whether the value of `SERVICE_VERSION` in the .env file is `Int` / `String`.) | Returns the service version |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/version
```

### POST Request
```url
http://{address}:{port}/version
```

## Response from API
```json
{
  "StatusCode": 200,
  "message": "Successful version information request",
  "data": {
    "RequestTime": "2024-03-26T05:23:11.411091",
    "Version": "1.0.0"
  }
}
```

## Error Response
The Version API is not error-prone, so if you get an error, it's probably coming from somewhere else.