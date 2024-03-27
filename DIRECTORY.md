# Directory structure
The directory structure of the AIpaca backend repository looks like this:
```
root
│
├── .env.example - Example configuration file.
├── .gitignore - List of files Git doesn't want to track.
├── app.py - Main file(Execute this file to run project).
├── env_manage.py - Python file that manages to import .env from subdirectories.
├── LICENSE - LICENSE info.
├── README.md - Project description.
├── StatusCode 번호.md - Info of Status Code.
│
├── .github/ - GitHub Issue/PR Templates.
│ ├── ISSUE_TEMPLATE/ - 이슈 템플릿.
│ └── PULL_REQUEST_TEMPLATE - PR 템플릿.
│
├── db/ - Setting up the database.
│ └── db_config.sample.py - Setting up the database sample file.
│
├── routes/ - API routes.
│ ├── api/ - API Endpoints.
│ │ ├── challenge/ - Achievements API.
│ │ │ ├── achieve/ - Achievements add API.
│ │ │ └── verify/ - Achievements verify API.
│ │ ├── detectlang/ - Detecting language API.
│ │ ├── evaluation/ - Evaluation API.
│ │ │ ├── gemini/ - Evaluation using Gemini API.
│ │ │ ├── gpt/ - Evaluation using GPT API.
│ │ │ └── prompt/ - Prompt directive.
│ │ ├── trans/ - 번역 API.
│ │ └── user/ - User API.
│ │      ├── login/ - Login API.
│ │      └── signup/ - Sign Up API.
│ ├── notice/ - Notice API.
│ ├── ping/ - Server check API.
│ ├── terms/ - Terms of Service API.
│ └── version/ - Service version information.
│
└── terms/ - Terms of use and privacy policy documentation.
      ├── en/ - English documentation.
      └── ko/ - Korean documentation.
```

# Basic structure
The names of the folders in the routes directory are the paths. For example, `routes/ping` will handle the `/ping` route.