# DevOps Lab Assignment 4 — News summary API

Student: Muhmmad Ali Arshad  
Registration: FA23-BDS-024  
Language: Python  
Assigned source: ProPakistani (`024 % 20 + 1 = 5`)

The container includes Python, Chrome for Testing, a matching ChromeDriver, Selenium, and a Flask REST API. Selenium searches the assigned news source for a keyword, loads the first result, extracts the article, and produces an extractive summary. Because ProPakistani rejects some cloud IP addresses, the application falls back to its public WordPress API and then to the public Jina Reader service when direct browsing fails.

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

## Optional AWS demo

The lab EC2 instance is in `ap-south-1` (Mumbai). Its current public address, checked on 31 October 2026, is:

```text
http://35.154.114.110:7000/get?keyword=technology
```

The public IP can change when the instance is stopped and started. The Docker image does not depend on this address: anyone can run the image on their own machine with `-p 7000:7000` and use `http://localhost:7000/`.

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

Alternatively, add a Docker Hub access token as the GitHub Actions repository secret `DOCKERHUB_TOKEN`, then run the **Build and publish Docker image** workflow from the Actions tab. The workflow builds and pushes the same image tag without requiring Docker on your own computer. Do not commit the token or paste it into the submission form.

Submission values:

- Name: Muhmmad Ali Arshad
- Registration Number: FA23-BDS-024
- GitHub Repo: `https://github.com/muhammad-ali-arshad/devops-lab4`
- Docker Hub Image Name with Tag: `ali024024/devops-lab4:fa23-bds-024`
- Development Environment: Python 3.12

Only submit the repo and image URLs after confirming both were actually published.
