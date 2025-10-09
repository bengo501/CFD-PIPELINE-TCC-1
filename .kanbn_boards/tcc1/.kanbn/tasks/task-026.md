---
name: integrar minio para armazenamento de artefatos
tags:
  - backend
  - storage
  - minio
created: 2025-10-09
assigned: 
sprint: mes 3 sem 3
atividades-tcc: a8
story-points: 5
---

# integrar minio para armazenamento de artefatos

implementar storage de objetos com minio para arquivos grandes.

## tarefas

### instalação e configuração
- [ ] instalar minio server
- [ ] configurar buckets
- [ ] configurar políticas de acesso
- [ ] configurar retenção

### buckets necessários
- [ ] `bed-files` (arquivos .bed e .bed.json)
- [ ] `3d-models` (arquivos .blend)
- [ ] `stl-exports` (arquivos .stl)
- [ ] `openfoam-cases` (casos completos)
- [ ] `simulation-results` (resultados vtk, csv)

### integração backend
- [ ] instalar minio python client
- [ ] criar `backend/app/services/storage_service.py`
- [ ] upload de arquivos
- [ ] download de arquivos
- [ ] geração de urls assinadas (presigned)
- [ ] listagem de arquivos
- [ ] exclusão de arquivos

### metadados no postgresql
- [ ] salvar paths/urls no banco
- [ ] relacionar arquivos com jobs
- [ ] índices para busca rápida

### api endpoints
- [ ] POST /api/files/upload
- [ ] GET /api/files/{file_id}
- [ ] GET /api/files/{file_id}/download
- [ ] DELETE /api/files/{file_id}
- [ ] GET /api/jobs/{job_id}/files

## estrutura de código

```python
# backend/app/services/storage_service.py
from minio import Minio

class StorageService:
    def __init__(self):
        self.client = Minio(
            "minio:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
    
    def upload_file(self, bucket, object_name, file_path):
        """upload arquivo para minio"""
        self.client.fput_object(bucket, object_name, file_path)
        return f"minio://{bucket}/{object_name}"
    
    def get_presigned_url(self, bucket, object_name, expires=3600):
        """gera url assinada para download"""
        return self.client.presigned_get_object(bucket, object_name, expires)
```

## docker-compose integration

```yaml
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    
volumes:
  minio_data:
```

## prioridade
média - importante para produção

## estimativa
1-2 dias (5 story points)

## critérios de aceitação
- [ ] minio instalado e rodando
- [ ] 5 buckets criados
- [ ] upload funcional
- [ ] download com urls assinadas
- [ ] integrado com api
- [ ] metadados no postgresql
- [ ] documentação completa

