# Papago Translate API Specs
Translate and return the value requested by the client using the Papago API.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/api/trans/papago |

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
| `ClientID` | Yes | `String` | Papago Translation Clilent ID key |
| `ClientSecret` | Yes | `String` | Papago Translation Clilent Secret key |
| `APIType` | Option | `String` | Enter `naver_cloud` if the API was issued by NAVER CLOUD PLATFORM, or `naver_cloud_gov` if it was issued by NAVER CLOUD PLATFORM for Government. If omitted, it is assumed to be `naver_cloud`. |

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
http://{address}:{port}/api/trans/papago?text=안녕하세요!&OriginalLang=ko&TranslatedLang=en&ClientID=Papago_Client_ID&ClientSecret=Papago_Client_Secret&APIType=naver_cloud
```

### POST Request
```json
{
    "text": "안녕하세요!",
    "OriginalLang": "ko",
    "TranslatedLang": "en",
    "ClientID": "Papago_Client_ID",
    "ClientSecret": "Papago_Client_Secret",
    "APIType": "naver_cloud"
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

### Invalid ClientID or ClientSecret values
If you enter an invalid ClientID or ClientSecret value, it outputs an error via message.

Example:
```json
{
  "StatusCode": 401,
  "message": "Invalid ClientID or ClientSecret value. Please check them.",
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
  "StatusCode": 5000,
  "message": "An error occurred during translation",
  "data": {
    "RequestTime": "2024-03-27T01:42:34.585811+00:00",
    "Error": "Error Message"
  }
}
```