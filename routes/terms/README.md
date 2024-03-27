# Terms API Specs
Reads the language value from the request header and returns the URL to the appropriate terms file. The language values we currently accept are `en` and `ko`. Note that `.env` must have a value of `DOMAIN`, otherwise it will be `None`.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/terms |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Language-Accept` | Example: `Language-Accept: ko-KR` / Assumed to be `en` if no value or not in the terms file list. |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| None | None | None | Does not require a value when requesting version information. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `{GET/POST} request processed. Hello, world!` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |
| `privacy_policy` | `String` | Returns the privacy policy terms file URL |
| `terms_of_service` | `String` | Returns the terms of service terms file URL |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/terms
```

### POST Request
```url
http://{address}:{port}/terms
```

## Response from API
### GET Response
```json
{
  "StatusCode": 200,
  "message": "GET request processed. Hello, world!",
  "data": {
    "RequestTime": "2024-03-26T05:31:14.496909+00:00",
    "privacy_policy": "http://test.com/terms/en/privacy_policy.md",
    "terms_of_service": "http://test.com/terms/en/terms_of_service.md"
  }
}
```

### POST Response
```json
{
  "StatusCode": 200,
  "message": "POST request processed. Hello, world!",
  "data": {
    "RequestTime": "2024-03-26T05:31:14.496909+00:00",
    "privacy_policy": "http://test.com/terms/en/privacy_policy.md",
    "terms_of_service": "http://test.com/terms/en/terms_of_service.md"
  }
}
```

## Error Response
The Version API is not error-prone, so if you get an error, it's probably coming from somewhere else.

# Caution
The `DOMAIN` value in the `.env` file must be present to display correctly; if it does not exist, it will be displayed as `None`.