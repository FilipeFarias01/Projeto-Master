from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Optional
from enum import Enum
from datetime import date


class StatusEnum(str, Enum):
    pendente = 'pendente'
    em_andamento = 'em_andamento'
    concluida = 'concluida'
    cancelada = 'cancelada'


class PrioridadeEnum(str, Enum):
    baixa = 'baixa'
    media = 'media'
    alta = 'alta'
    critica = 'critica'


def normalizar_tags(tags: list[str]) -> list[str]:
    resultado = []
    for tag in tags:
        tag = tag.strip().lower()
        if tag and tag not in resultado:
            resultado.append(tag)
    return resultado


class TarefaEntrada(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'titulo': 'Implementar autenticacao JWT',
                'descricao': 'Adicionar login com token na API',
                'responsavel': 'Carlos Silva',
                'prioridade': 'alta',
                'status': 'pendente',
                'prazo': '2026-12-31',
                'tags': ['Python', 'API']
            }
        }
    )

    titulo: str
    descricao: Optional[str] = None
    responsavel: Optional[str] = None
    prioridade: PrioridadeEnum = PrioridadeEnum.media
    status: StatusEnum = StatusEnum.pendente
    prazo: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, valor: str) -> str:
        valor = valor.strip()

        if len(valor) < 3:
            raise ValueError('O titulo deve ter pelo menos 3 caracteres')

        if len(valor) > 120:
            raise ValueError('O titulo deve ter no maximo 120 caracteres')

        return valor

    @field_validator('responsavel')
    @classmethod
    def validar_responsavel(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            valor = valor.strip()

            if len(valor) < 2:
                raise ValueError(
                    'Nome do responsavel deve ter pelo menos 2 caracteres'
                )

            return valor.title()

        return valor

    @field_validator('tags')
    @classmethod
    def validar_tags(cls, valor: list[str]) -> list[str]:
        return normalizar_tags(valor)


class TarefaSaida(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    responsavel: Optional[str] = None
    prioridade: PrioridadeEnum
    status: StatusEnum
    prazo: Optional[date] = None
    criado_em: date = Field(default_factory=date.today)
    tags: list[str] = Field(default_factory=list)

    @field_validator('tags')
    @classmethod
    def validar_tags(cls, valor: list[str]) -> list[str]:
        return normalizar_tags(valor)


class TarefaParcial(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    responsavel: Optional[str] = None
    prioridade: Optional[PrioridadeEnum] = None
    status: Optional[StatusEnum] = None
    prazo: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator('tags')
    @classmethod
    def validar_tags(cls, valor: Optional[list[str]]) -> Optional[list[str]]:
        if valor is None:
            return valor
        return normalizar_tags(valor)


class StatusAtualizacao(BaseModel):
    status: StatusEnum
