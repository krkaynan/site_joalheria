# 🛒 E-commerce em Django & Vanilla JS

Uma aplicação de e-commerce produtiva, modular e fácil de manter. Construída com um backend sólido em Django e uma API leve, este projeto foi desenhado para escalar facilmente e permitir futuras integrações (como SPAs ou aplicativos mobile), mantendo a lógica de negócios segura no servidor.

## 🚀 Tecnologias e Stack

**Backend & Core:**

* **Linguagem:** Python
* **Framework:** Django (Templates server-side, ORM)
* **APIs:** REST / JSON (Endpoints leves)

**Frontend:**

* **Linguagem:** JavaScript (Vanilla JS), HTML5, CSS3
* **Interatividade:** Chamadas AJAX, Carrinho Persistente (Session/LocalStorage)
* **Performance:** Imagens otimizadas (WebP, `srcset`), Lazy Loading

**Infraestrutura, DevOps & Segurança:**

* **Servidores:** Gunicorn + Nginx
* **CI/CD:** Pipeline automatizado para Linting e Testes
* **Segurança:** Validação Server-side, Proteção CSRF, Hashing de senhas padrão Django

---

## 🏗️ Modelagem e Arquitetura de Dados

O banco de dados foi estruturado através do ORM do Django para garantir a integridade das regras de negócio. 

---

## 🧠 Decisões Arquiteturais

* **Lógica no Backend:** Toda a regra de preços, validações e carrinho crítico é mantida e validada no servidor via ORM para evitar manipulações indevidas no lado do cliente (client-side tampering).
* **Desacoplamento Planejado:** A comunicação do carrinho e checkout via endpoints REST/JSON foi projetada de forma leve para permitir uma futura separação do frontend (migração para React/Vue/Angular ou App Mobile).
* **Autonomia para a Operação:** O **Django Admin** foi altamente customizado. Isso permite que a equipe comercial e de operações gerencie o catálogo de produtos e os pedidos com facilidade, sem a necessidade de novos deploys por parte da equipe de engenharia.

---

## ⚙️ Funcionalidades em Destaque

* **Catálogo Dinâmico:** Fichas de produtos ricas com seleção dinâmica de variações (tamanho).
* **Checkout Fluido:** Integração AJAX para adição de itens, atualização de carrinho e finalização de compra sem recarregar a página desnecessariamente.
* **Testes Automatizados:** Alta cobertura de testes em fluxos críticos de negócio (adicionar ao carrinho, criação de pedido).

---

## 🛠️ Como rodar o projeto localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repositorio.git](https://github.com/krkaynan/site_joalheria.git

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações do banco de dados
python manage.py migrate

# Inicie o servidor local
python manage.py runserver

```
