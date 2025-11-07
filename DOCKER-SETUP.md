# Docker Configuration - Frontend & Backend Setup

## Estrutura Revisada

O projeto agora usa multi-stage builds otimizados para ambos frontend e backend:

### Frontend (React + Vite + Nginx)
- **Build Context**: Raiz do projeto (`.`)
- **Dockerfile**: `frontend/Dockerfile`
- **Porta**: 3000
- **Features**:
  - Multi-stage build (builder + runtime)
  - Nginx com SPA routing configurado
  - Cache de assets estáticos (1 ano)
  - Gzip compression habilitado
  - Health checks

### Backend (FastAPI + Python)
- **Build Context**: Raiz do projeto (`.`)
- **Dockerfile**: `backend/Dockerfile`
- **Porta**: 8000
- **Features**:
  - Multi-stage build (builder + runtime)
  - Virtual environment otimizado
  - Dependências apenas de runtime
  - Uvicorn com reload

## Executar os containers

```bash
# Build e start dos containers
docker-compose up --build

# Parar os containers
docker-compose down

# Ver logs
docker-compose logs -f frontend
docker-compose logs -f backend
```

## URLs de Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/api/health

## Otimizações Aplicadas

1. **Multi-stage builds**: Reduz tamanho final das imagens
2. **.dockerignore**: Evita copiar arquivos desnecessários
3. **Alpine Linux**: Imagens menores e mais seguras
4. **Nginx SPA routing**: Suporta client-side routing do React
5. **Health checks**: Verifica se containers estão saudáveis
6. **Rede Docker**: Frontend e backend se comunicam através da rede `naviacess-network`

## Troubleshooting

Se encontrar problemas:

```bash
# Limpar containers e volumes
docker-compose down -v

# Rebuildar sem cache
docker-compose build --no-cache

# Verificar logs detalhados
docker-compose logs -f
```
