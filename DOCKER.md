# 🐳 Docker Setup - NaviAcess

## Overview
Complete Docker configuration for NaviAcess with:
- **Backend**: FastAPI em contêiner Python
- **Frontend**: React + Vite servido por Nginx
- **Orquestração**: Docker Compose para ambiente dev/prod

## Arquivos Criados

### 1. **backend/Dockerfile**
Multi-stage build otimizado para FastAPI:
- Builder stage: Compila dependências Python
- Runtime stage: Imagem slim apenas com essencial
- Health check automático
- Porta: 8000

### 2. **frontend/Dockerfile**
Multi-stage build otimizado para React:
- Builder stage: Node com npm ci + build Vite
- Runtime stage: Nginx alpine para servir SPA
- Compressão gzip automática
- Porta: 80, 443

### 3. **docker-compose.yml**
Orquestra ambos os serviços:
- Backend rodando em http://localhost:8000
- Frontend rodando em http://localhost
- Network bridge para comunicação entre containers
- Health checks automáticos
- Volumes para desenvolvimento

### 4. **nginx.conf**
Configuração Nginx avançada:
- SPA routing (try_files para Client-Side routing)
- Proxy reverso para backend (/api/ → backend:8000)
- Caching de assets estáticos
- Compressão gzip
- Headers de segurança (X-Frame-Options, CSP, etc)
- Cache control inteligente

### 5. **.dockerignore**
Arquivo para excluir arquivos desnecessários da build

## Como Usar

### Build das Imagens
```bash
docker-compose build
```

### Iniciar Ambiente Completo
```bash
docker-compose up
```

### Iniciar em Background
```bash
docker-compose up -d
```

### Ver Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f  # todos os serviços
```

### Parar Serviços
```bash
docker-compose down
```

### Rebuild de um Serviço Específico
```bash
docker-compose up --build backend
docker-compose up --build frontend
```

## URLs de Acesso

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://localhost | Interface React |
| Backend | http://localhost:8000 | API FastAPI |
| Docs FastAPI | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc documentação |

## Ambiente Development vs Production

### Development (Padrão)
- Volume mounts para hot-reload
- Logging detalhado
- Debug habilitado

### Production
```bash
# Remover volumes
docker-compose -f docker-compose.yml down

# Buildar sem reload
docker-compose build --no-cache
```

## Variáveis de Ambiente

Backend (`backend/`):
```env
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
API_ENV=development
```

## Troubleshooting

### Porta 80 em uso
```bash
# Ver processos na porta 80
netstat -ano | findstr :80  # Windows
lsof -i :80                 # Mac/Linux
```

### Rebuild completo
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build
```

### Limpar Docker
```bash
docker system prune -a
docker volume prune
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │   Frontend       │      │   Backend        │    │
│  │ ┌──────────────┐ │      │ ┌──────────────┐ │    │
│  │ │  React/Vite │ │      │ │   FastAPI    │ │    │
│  │ │    nginx     │ │◄────►│ │   Uvicorn   │ │    │
│  │ │   Port 80   │ │      │ │  Port 8000  │ │    │
│  │ └──────────────┘ │      │ └──────────────┘ │    │
│  └──────────────────┘      └──────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Próximas Melhorias
- [ ] Suporte a HTTPS com Let's Encrypt
- [ ] Database service (PostgreSQL)
- [ ] Redis para cache
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment
- [ ] Environment variables .env
- [ ] Docker registry push

## Comandos Úteis

```bash
# Verificar status dos containers
docker-compose ps

# Executar comando em container
docker-compose exec backend bash
docker-compose exec frontend sh

# Ver uso de recursos
docker stats

# Inspecionar network
docker network inspect <network-name>

# Limpar tudo
docker-compose down -v --remove-orphans
```

---
**Criado**: 2025-11-07  
**Versão**: 1.0  
**Status**: ✅ Pronto para uso
