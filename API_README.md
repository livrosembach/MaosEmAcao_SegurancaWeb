# Documentação da API REST - Mãos em Ação

Esta documentação serve de referência para desenvolvedores Frontend integrarem suas telas com o Backend da plataforma **Mãos em Ação**.

---

## 🔐 Autenticação e CSRF no Frontend

O backend utiliza a autenticação de sessão padrão do Django integrada ao AWS Cognito.

1. **Autenticação:** 
   O fluxo de autenticação é feito via Cookies de Sessão (`sessionid`). Quando o usuário loga pelo Cognito, o navegador gerencia e envia esse cookie automaticamente em todas as chamadas HTTP para a mesma origem.
2. **Proteção contra CSRF:**
   Para operações que alteram dados (`POST`, `PUT`, `PATCH`, `DELETE`), o Django exige o cabeçalho `X-CSRFToken` para evitar ataques Cross-Site Request Forgery.
   *   **Como obter:** Chame `GET /api/csrf/`. Isso fará com que o Django defina o cookie `csrftoken` na resposta.
   *   **Como enviar:** Leia o cookie `csrftoken` usando JavaScript (ou use bibliotecas como o Axios, que configuram isso nativamente) e envie o token no header `X-CSRFToken` em todas as chamadas modificadoras de estado.

---

## 📌 Endpoints da API

A URL base da API é a mesma do servidor Django (ex: `http://localhost:8000`).

---

### 1. CSRF Token Setup
Define o cookie `csrftoken` para que a aplicação possa lê-lo e enviá-lo nas chamadas de escrita.

*   **Método:** `GET`
*   **Endpoint:** `/api/csrf/`
*   **Resposta (200 OK):**
    ```json
    {
      "detail": "CSRF cookie set."
    }
    ```

---

### 2. Perfis (`/api/profile/`)

#### Obter Informações do Perfil Logado
Retorna o perfil do usuário atualmente autenticado.

*   **Método:** `GET`
*   **Endpoint:** `/api/profile/`
*   **Resposta caso o usuário ainda não possua perfil criado (200 OK):**
    ```json
    {
      "has_profile": false,
      "email": "usuario@exemplo.com",
      "username": "usuario123"
    }
    ```
*   **Resposta caso seja perfil Voluntário (200 OK):**
    ```json
    {
      "has_profile": true,
      "role": "VOLUNTEER",
      "email": "voluntario@exemplo.com",
      "username": "voluntario123",
      "cpf": "12345678901",
      "phone": "(11) 99999-9999",
      "bio": "Estudante interessado em ajudar a comunidade local."
    }
    ```
*   **Resposta caso seja perfil ONG (200 OK):**
    ```json
    {
      "has_profile": true,
      "role": "NGO",
      "email": "ong@exemplo.com",
      "username": "ong_inclusao",
      "cnpj": "12345678000199",
      "phone": "(11) 5555-5555",
      "address": "Av. Paulista, 1000 - São Paulo, SP",
      "description": "ONG focada em ensinar programação para jovens carentes."
    }
    ```
*   **Erro se não autenticado (401 Unauthorized):**
    ```json
    { "error": "Autenticação necessária." }
    ```

#### Criar Perfil (Primeiro Acesso)
Cadastra os dados do perfil após o login inicial.

*   **Método:** `POST`
*   **Endpoint:** `/api/profile/`
*   **Headers:** `Content-Type: application/json`
*   **Payload (Voluntário):**
    ```json
    {
      "role": "VOLUNTEER",
      "cpf": "12345678901",
      "phone": "(11) 99999-9999",
      "bio": "Interesse em causas animais."
    }
    ```
*   **Payload (ONG):**
    ```json
    {
      "role": "NGO",
      "cnpj": "12345678000199",
      "phone": "(11) 5555-5555",
      "address": "Rua da ONG, 123",
      "description": "ONG de resgate de cães de rua."
    }
    ```
*   **Respostas:**
    - `201 Created`: Perfil criado. Ex: `{"message": "Perfil criado com sucesso!", "role": "VOLUNTEER"}`
    - `400 Bad Request`: Parâmetros obrigatórios em falta ou inválidos, ou perfil já existente.

#### Atualizar Perfil Logado
Atualiza dados cadastrais.

*   **Método:** `PUT`
*   **Endpoint:** `/api/profile/`
*   **Headers:** `Content-Type: application/json`
*   **Payload (Qualquer campo de perfil é opcional):**
    ```json
    {
      "phone": "(11) 98888-8888",
      "bio": "Nova biografia do voluntário."
    }
    ```
*   **Resposta (200 OK):**
    ```json
    {
      "message": "Perfil atualizado com sucesso!"
    }
    ```

---

### 3. Vagas (`/api/vacancies/`)

#### Listar Vagas
Retorna todas as vagas disponíveis na plataforma.

*   **Método:** `GET`
*   **Endpoint:** `/api/vacancies/`
*   **Resposta (200 OK):**
    ```json
    [
      {
        "id": 1,
        "title": "Aulas de Programação Básica",
        "description": "Ensinar lógica de programação e Scratch.",
        "requirements": "Boa comunicação e lógica básica.",
        "created_at": "2026-06-11T12:00:00Z",
        "ngo": {
          "name": "ong_inclusao",
          "description": "ONG focada em ensinar programação."
        }
      }
    ]
    ```

#### Criar Vaga *(Apenas ONGs)*
Cria uma nova oportunidade de voluntariado.

*   **Método:** `POST`
*   **Endpoint:** `/api/vacancies/`
*   **Headers:** `Content-Type: application/json`
*   **Payload:**
    ```json
    {
      "title": "Aulas de Programação Básica",
      "description": "Ensinar lógica de programação e Scratch.",
      "requirements": "Boa comunicação e lógica básica."
    }
    ```
*   **Respostas:**
    - `201 Created`: Vaga criada. Ex: `{"message": "Vaga criada com sucesso!", "vacancy_id": 1}`
    - `403 Forbidden`: Se o perfil logado não for uma ONG.

#### Obter Detalhes da Vaga
*   **Método:** `GET`
*   **Endpoint:** `/api/vacancies/<id_da_vaga>/`
*   **Resposta (200 OK):**
    ```json
    {
      "id": 1,
      "title": "Aulas de Programação Básica",
      "description": "Ensinar lógica de programação e Scratch.",
      "requirements": "Boa comunicação e lógica básica.",
      "created_at": "2026-06-11T12:00:00Z",
      "ngo": {
        "name": "ong_inclusao",
        "description": "ONG focada em ensinar programação."
      }
    }
    ```

#### Editar Vaga *(Apenas a ONG que a criou)*
*   **Método:** `PUT`
*   **Endpoint:** `/api/vacancies/<id_da_vaga>/`
*   **Payload:** Campos JSON que deseja atualizar (ex: `title`, `description`).
*   **Resposta (200 OK):**
    ```json
    {
      "message": "Vaga atualizada com sucesso!"
    }
    ```

#### Excluir Vaga *(Apenas a ONG que a criou)*
*   **Método:** `DELETE`
*   **Endpoint:** `/api/vacancies/<id_da_vaga>/`
*   **Resposta (200 OK):**
    ```json
    {
      "message": "Vaga deletada com sucesso!"
    }
    ```

---

### 4. Candidaturas (`/api/applications/`)

#### Candidatar-se a uma Vaga *(Apenas Voluntários)*
Cria uma candidatura com status inicial `PENDING` (Pendente).

*   **Método:** `POST`
*   **Endpoint:** `/api/vacancies/<id_da_vaga>/apply/`
*   **Respostas:**
    - `201 Created`: Candidatura enviada. `{"message": "Candidatura enviada com sucesso!"}`
    - `400 Bad Request`: Se o voluntário já tiver se candidatado a esta vaga anteriormente.
    - `403 Forbidden`: Se o perfil logado não for um Voluntário.

#### Listar Candidaturas
Retorna as candidaturas conforme o tipo de perfil logado.

*   **Método:** `GET`
*   **Endpoint:** `/api/applications/`
*   **Resposta se for Voluntário (200 OK):**
    *(Retorna as vagas para as quais você se candidatou e seus respectivos status)*
    ```json
    [
      {
        "id": 5,
        "status": "PENDING",
        "applied_at": "2026-06-11T12:30:00Z",
        "vacancy": {
          "id": 1,
          "title": "Aulas de Programação Básica",
          "ngo_name": "ong_inclusao"
        }
      }
    ]
    ```
*   **Resposta se for ONG (200 OK):**
    *(Retorna todas as candidaturas recebidas nas suas vagas, revelando os dados de contato do voluntário)*
    ```json
    [
      {
        "id": 5,
        "status": "PENDING",
        "applied_at": "2026-06-11T12:30:00Z",
        "vacancy": {
          "id": 1,
          "title": "Aulas de Programação Básica"
        },
        "volunteer": {
          "username": "voluntario123",
          "email": "voluntario@exemplo.com",
          "phone": "(11) 99999-9999",
          "bio": "Estudante interessado em ajudar a comunidade local."
        }
      }
    ]
    ```

#### Aprovar ou Rejeitar Candidatura *(Apenas a ONG dona da vaga)*
Altera o status da candidatura para aceito ou rejeitado.

*   **Método:** `PATCH`
*   **Endpoint:** `/api/applications/<id_da_candidatura>/`
*   **Payload:**
    ```json
    {
      "status": "ACCEPTED" 
    }
    ```
    *(Valores aceitos para status: `ACCEPTED` ou `REJECTED`)*
*   **Resposta (200 OK):**
    ```json
    {
      "message": "Candidatura atualizada para: Aceito."
    }
    ```

#### Cancelar Candidatura *(Apenas o Voluntário criador)*
Remove a candidatura da plataforma.

*   **Método:** `DELETE`
*   **Endpoint:** `/api/applications/<id_da_candidatura>/`
*   **Resposta (200 OK):**
    ```json
    {
      "message": "Candidatura cancelada com sucesso."
    }
    ```
