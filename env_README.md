# env file
The `.env` file is responsible for the values that are set when the project is run. Some items will work by default without being set in the `.env` file, but other values are required and are recommended to be set. Simply modify the contents of the `.env.sample` file as appropriate and rename it to `.env`.

# env file struct
```env
DOMAIN=

FLASK_RUN_PORT=
LIBRE_TRANSLATE_API=
SERVICE_VERSION=
NOTICE_RSS_URL=
CACHE_DURATION_MINUTES=
TIMEZONE=
```

* `DOMAIN`: Enter the domain address that is reachable when the project runs. The port number should also be entered, with no forward slashes (`/`) at the end. When returning the terms file, the URL of the terms file is returned, which is used for the domain part.
  - Example: `DOMAIN="https://test.com"`
  - It is a string, it must be enclosed in double quotes (`""`).
* `FLASK_RUN_PORT`: The port number to use when the Flask server is running. If omitted, use port `5000`.
  - Example: `FLASK_RUN_PORT=5005`
* `LIBRE_TRANSLATE_API`: Enter the domain address of the server providing the Libre Translate API. For a list of publicly available API mirror server domains, use [libretranslatepy - LibreTranslate Mirrors](https://github.com/argosopentech/LibreTranslate-py?tab=readme-ov-file#libretranslate-mirrors) or [Official API](https://portal.libretranslate.com)!
  - Example: `LIBRE_TRANSLATE_API=https://libretranslate-api-server.com`
* `SERVICE_VERSION`: Enter the service version. Used in the version return API part.
   - Example: `SERVICE_VERSION="1.0.0"`
* `NOTICE_RSS_URL`: The URL of where the announcement RSS is available.
   - Example: `NOTICE_RSS_URL="https://notice-domain.com/rss`
* `CACHE_DURATION_MINUTES`: How long to cache announcement information for. The unit is minutes.
  - Example: `CACHE_DURATION_MINUTES=180`
* `TIMEZONE`: HSet the time zone. Used in the verification portion of the achievement registration.
  - Example: `TIMEZONE="UTC+9"`