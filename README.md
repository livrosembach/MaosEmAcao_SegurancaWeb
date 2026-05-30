# MaosEmAcao_SegurancaWeb

entra no env instala as parada roda "aws login" e dai python manage.py runserver

## Cognito settings

This project loads Cognito settings from AWS SSM Parameter Store. Ensure AWS
credentials and region configuration are available to the app.

| Setting | Default SSM parameter |
| --- | --- |
| COGNITO_APP_CLIENT_ID | /maosemacao/cognito/cognito_client_id |
| COGNITO_APP_CLIENT_SECRET | /maosemacao/cognito/cognito_client_secret |
| COGNITO_DOMAIN | /maosemacao/cognito/cognito_domain |

Set `COGNITO_APP_CLIENT_ID`, `COGNITO_APP_CLIENT_SECRET`, and `COGNITO_DOMAIN`
to bypass SSM. Override parameter names with `COGNITO_APP_CLIENT_ID_SSM`,
`COGNITO_APP_CLIENT_SECRET_SSM`, and `COGNITO_DOMAIN_SSM`.

