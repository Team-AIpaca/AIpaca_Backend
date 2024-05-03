# OpenAI GPT AI Evalation API Specs
API for evaluating translations with the OpenAI GPT API.

# Request
| HTTP Method | Request URL |
|-------------|-------------|
| `POST` | http://{address}:{port}/api/evaluation/gpt |

## Request Header
| Header Name | Notes |
|-------------|-------|
| `Content-Type` | `Content-Type: application/json` |

## Request Body
| Field Name | Required | Type | Notes |
|------------|----------|------|-------|
| `OpenAIAPIKey` | Yes | `String` | API keys for the OpenAI API |
| `GPTVersion` | Yes | `String` | Write the GPT model name. You can find available models at [Models - OpenAI API](https://platform.openai.com/docs/models/overview). You must use GPT-3.5 or GPT-4. |
| `Original` | Yes | `String` | Original text. Escape sequences must be preceded by a backslash (\). |
| `OriginalLang` | Yes | `String` | `Original`'s language code. The `ISO 639-1` code, which must be lowercase. |
| `Translated` | Yes | `String` | Translated text. Escape sequences must be preceded by a backslash (\). |
| `TranslatedLang` | Yes | `String` | `Translated`'s language code. The `ISO 639-1` code, which must be lowercase. |
| `EvaluationLang` | Yes | `String` | Language preferences when response evaluations |

# Response
## Response Body
| Field Name | Type | Notes |
|------------|----------|------|
| `StatusCode` | `Int` | Return `200` on successful request processing |
| `message` | `String` | Return `Success to request to Gemini!` message on successful request processing |
| `RequestTime` | `String` | Returns the date and time value at the time the request was sent |
| `result` | `String` | The `result` key contains `Score`, `RecommandedTrans`, and `Rating`. |

# Example
## Request to API
### POST Request
```json
{
    "OpenAIAPIKey": "OpenAI_API_Key_Here",
	"GPTVersion": "GPT_Model_Name_Here_Example_gpt-4-turbo-preview",
    "Original": "안녕하세요. 반갑습니다. 저는 케빈입니다.",
    "OriginalLang": "ko",
    "Translated": "Hello, Nice to meet you. My name is Kevin.",
    "TranslatedLang": "en",
    "EvaluationLang": "ko"
}
```

## Response from API
### POST Response
```json
{
	"StatusCode": 200,
	"message": "Success to request to Gemini!",
	"data": {
		"RequestTime": "2024-03-31T05:19:41.316298+00:00",
		"result": {
			"Score": 95,
			"RecommandedTrans": "Hello, Nice to meet you. My name is Kevin.",
			"Rating": "번역은 우수하며 원문의 느낌과 의미를 잘 전달했습니다. 번역은 정확하고 자연스러우며, 원문의 뉘앙스도 잘 살려내고 있습니다."
		}
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
    "MissingFields": "TranslatedLang",
    "UnknownParams": "TranslatedLangs"
  }
}
```

### Response the request If there is a mismatch between the language value entered and the actual language code
If there is a mismatch between the entered language value and the actual language code, output which field is different.

Example:
```json
{
  "StatusCode": 4004,
  "message": "A value is not allowed in ko: en",
  "data": {
    "RequestTime": "2024-03-27T03:01:32.913821+00:00"
  }
}
```

### Invalid API Key
Outputs an error if an invalid API key is entered.

Example:
```json
{
  "StatusCode": 4200,
  "message": "Invalid API Key. Please check API Key.",
  "data": {
    "RequestTime": "2024-03-27T02:56:35.217018+00:00"
  }
}
```

### Response the request in the wrong language(Temporary holds)
Returns which items in the data key sent the request in the wrong language (by Gemini), for each item in the data key.

* `mismatchTransLang`: Returns `no` if the `TranslatedLang` value matches the language code in `RecommandedTrans`, or `yes` if it does not.
* `mismatchEvaluationLang`: Returns `no` if the `EvaluationLang` value matches the language code in `Rating`, or `yes` if it does not.


Example:
```json
{
  "StatusCode": 5204,
  "message": "Output from the Gemini API in a different language to the one requested by the user",
  "data": {
    "RequestTime": "2024-03-27T03:01:32.913821+00:00",
    "mismatchTransLang": "yes",
    "mismatchEvaluationLang": "no"
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