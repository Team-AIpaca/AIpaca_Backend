# LibreTranslate API Specs
Translate and return the value requested by the client using the LibreTranslate API.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/api/trans/libretranslate |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `text` | Yes | `String` | It must contain the text you want to translate. |
| `OriginalLang` | Yes | `String` | The language code of `text`. The `ISO 639-1` code, which must be lowercase. |
| `TranslatedLang` | Yes | `String` | The language code of the language you want to be translated into. The `ISO 639-1` code, which must be lowercase. |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Translation successful` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |
| `result` | `String` | Contains the translated text value. |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/api/trans/libretranslate?text=안녕하세요!&OriginalLang=ko&TranslatedLang=en
```

### POST Request
```json
{
    "text": "안녕하세요!",
    "OriginalLang": "ko",
    "TranslatedLang": "en"
}
```

## Response from API
### GET Response
```json
{
  "StatusCode": 200,
  "message": "Translation successful",
  "data": {
    "RequestTime": "2024-03-26T10:22:19.032571+00:00",
    "result": {
      "Translation": "Hello!"
    }
  }
}
```

### POST Response
```json
{
  "StatusCode": 200,
  "message": "Translation successful",
  "data": {
    "RequestTime": "2024-03-26T10:22:19.032571+00:00",
    "result": {
      "Translation": "Hello!"
    }
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