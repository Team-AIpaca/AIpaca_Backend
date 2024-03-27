# Language Detect API Specs
An API that takes in text and returns you what language to return it in.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/api/detectlang |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `text` | Yes | `String` | Enter the text you want to know what language it's in. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Success to get language code!` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |
| `result` | `String` | Returns what language `text` is in. |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/api/trans/detectlang?text=안녕하세요!
```

### POST Request
```json
{
    "text": "안녕하세요!",
}
```

## Response from API
### GET Response
```json
{
  "StatusCode": 200,
  "message": "Success to get language code!",
  "data": {
    "RequestTime": "2024-03-26T12:36:12.908656+00:00",
    "result": "ko"
  }
}
```

### POST Response
```json
{
  "StatusCode": 200,
  "message": "Success to get language code!",
  "data": {
    "RequestTime": "2024-03-26T12:36:12.908656+00:00",
    "result": "ko"
  }
}
```

## Error Response
### Required field not filled in / Unknown field filled in
Missing required fields are listed in MissingFields, and unknown fields are listed in UnknownParams.

Example:
```json
{
  "StatusCode": 4003,
  "message": "Missing fields and Unknown parameters",
  "data": {
    "RequestTime": "2024-03-26T10:30:55.487194+00:00",
    "MissingFields": "TranslatedLang",
    "UnknownParams": "TranslatedLangs"
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