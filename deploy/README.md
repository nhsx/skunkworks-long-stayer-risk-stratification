# Build + Deployment Files

| File | Description |
| ---- | ----------- |
| [LTSS_API.Dockerfile](LTSS_API.Dockerfile) | Dockerfile for building the backend API Flask app container |
| [LTSS_WebUI.Dockerfile](LTSS_WebUI.Dockerfile) | Dockerfile for building the WebUI container |
| [ltss.nginx.conf](ltss.nginx.conf) | Nnginx configuration required by the WebUI container to correctly proxy API calls to the API container |
| [uwsgi.ini](uwsgi.ini) | Uwsgi configuration required by the API container to instruct uwsgi how to launch the Flask app |
