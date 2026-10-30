# DevOps Lab Assignment 4 — News summary API

Student: Muhmmad Ali Arshad  
Registration: FA23-BDS-024  
Language: Python  
Assigned source: ProPakistani (`024 % 20 + 1 = 5`)

The container includes Python, Chrome for Testing, a matching ChromeDriver, Selenium, and a Flask REST API. Selenium searches the assigned news source for a keyword, loads the first result, extracts the article, and produces an extractive summary.

## Build and run

```bash
docker build -t ali024024/devops-lab4:fa23-bds-024 .
docker run --rm -p 7000:7000 ali024024/devops-lab4:fa23-bds-024
```

Check the page and API:

```bash
curl http://localhost:7000/
curl http://localhost:7000/health
curl 'http://localhost:7000/get?keyword=technology'
```

The root page shows the registration number. `/get` returns JSON with `registration`, `newssource`, `keyword`, `url`, and `summary`. It returns HTTP 400 for a missing or oversized keyword and HTTP 502 if the search engine or article cannot be accessed. External sites can change their markup or block automation.

## Publish

```bash
git init
git add .
git commit -m "Build Selenium news summary API"
git branch -M main
gh repo create muhammad-ali-arshad/devops-lab4 --public --source . --push
docker login
docker push ali024024/devops-lab4:fa23-bds-024
```

Submission values:

- Name: Muhmmad Ali Arshad
- Registration Number: FA23-BDS-024
- GitHub Repo: `https://github.com/muhammad-ali-arshad/devops-lab4`
- Docker Hub Image Name with Tag: `ali024024/devops-lab4:fa23-bds-024`
- Development Environment: Python 3.12

Only submit the repo and image URLs after confirming both were actually published.
