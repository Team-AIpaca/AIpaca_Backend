# Service Notice API Specs
Service announcement return API. Reads and returns RSS. Connects to the RSS address in `NOTICE_RSS_URL` of `.env` and gets the value.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `GET` or `POST` | http://{address}:{port}/notice |

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
| `message` | `String` | Return `Successful Notice information request` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |
| `Notice` | `String` | Values returned by Notice RSS. Value depends on the value in RSS. |

# Example
## Request to API
### GET Request
```url
http://{address}:{port}/notice
```

### POST Request
```url
http://{address}:{port}/notice
```

## Response from API
### GET Response
```json
{
  "StatusCode": 200,
  "message": "Successful Notice information request",
  "data": {
    "RequestTime": "2024-03-26T09:50:05.840647+00:00",
    "Notice": {
        "notice": "contents(Example)"
        }
    }
}
```

### POST Response
```json
{
  "StatusCode": 200,
  "message": "Successful Notice information request",
  "data": {
    "RequestTime": "2024-03-26T09:50:05.840647+00:00",
    "Notice": {
        "notice": "contents(Example)"
        }
    }
}
```

## Error Response
The Version API is not error-prone, so if you get an error, it's probably coming from somewhere else.

# Warning
## Failed to get the notice RSS value
If the notice RSS value was not fetched, an error message might be displayed.

## CACHE_DURATION_MINUTES is not set
If the value of `CACHE_DURATION_MINUTES` cannot be obtained from `.env`, it may output `CACHE_DURATION_MINUTES is not set.`.

## Returning cached data
It will cache for as long as the `CACHE_DURATION_MINUTES` in `.env` says, so if RSS is updated before the cache expires, it won't get the latest information.

## Cache directory and files
Cache files are stored in the `cache` directory in the format `{yyyymmdd_hhMMss}_language code.json`. Example: `20240326185838_ko-KR.json`

The `cache` directory is created if it doesn't exist, and expired cache files are checked and deleted when new requests come in.