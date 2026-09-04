from fastapi import APIRouter, HTTPException, Path, Query, Response
from typing import Annotated, Optional

from app.models import (
    TarefaEntrada,
    TarefaSaida,
    TarefaParcial,
    StatusAtualizacao,
    StatusEnum,
    PrioridadeEnum
)


router = APIRouter(
    prefix='/tarefas',
    tags=['Tarefas']
)


banco: list[TarefaSaida] = [
    TarefaSaida(
        id=1,
        titulo='Configurar ambiente Python',
        descricao='Preparar o ambiente para desenvolvimento',
        responsavel='Carlos',
        prioridade='alta',
        status='concluida',
        tags=['Python', 'Ambiente']
    ),
    TarefaSaida(
        id=2,
        titulo='Criar modelos Pydantic',
        descricao='Criar os modelos de entrada e saida',
        responsavel='Ana',
        prioridade='alta',
        status='concluida',
        tags=['Pydantic', 'Python']
    ),
    TarefaSaida(
        id=3,
        titulo='Implementar CRUD completo',
        descricao='Criar todas as rotas da API',
        responsavel='Carlos',
        prioridade='critica',
        status='em_andamento',
        tags=['CRUD', 'API', 'FastAPI']
    ),
    TarefaSaida(
        id=4,
        titulo='Conectar ao banco MySQL',
        descricao='Configurar conexao da API com MySQL',
        responsavel='Bruno',
        prioridade='alta',
        status='pendente',
        tags=['MySQL', 'Banco']
    ),
    TarefaSaida(
        id=5,
        titulo='Escrever documentacao',
        descricao='Criar documentacao do projeto',
        responsavel='Ana',
        prioridade='baixa',
        status='pendente',
        tags=['Documentacao']
    )
]


proximo_id = 6


@router.get(
    '/estatisticas',
    summary='Estatisticas gerais das tarefas'
)
def estatisticas():
    por_status = {
        status.value: sum(
            1
            for tarefa in banco
            if tarefa.status == status
        )
        for status in StatusEnum
    }

    por_prioridade = {
        prioridade.value: sum(
            1
            for tarefa in banco
            if tarefa.prioridade == prioridade
        )
        for prioridade in PrioridadeEnum
    }

    return {
        'total': len(banco),
        'por_status': por_status,
        'por_prioridade': por_prioridade
    }


@router.get(
    '/prioridade/critica',
    response_model=list[TarefaSaida],
    summary='Lista tarefas criticas em aberto'
)
def listar_tarefas_criticas():
    return [
        tarefa
        for tarefa in banco
        if (
            tarefa.prioridade == PrioridadeEnum.critica
            and tarefa.status not in [
                StatusEnum.concluida,
                StatusEnum.cancelada
            ]
        )
    ]


@router.get(
    '/responsavel/{nome}',
    response_model=list[TarefaSaida],
    summary='Busca tarefas pelo responsavel'
)
def buscar_por_responsavel(
    nome: Annotated[
        str,
        Path(min_length=2, description='Nome do responsavel')
    ]
):
    resultado = [
        tarefa
        for tarefa in banco
        if (
            tarefa.responsavel is not None
            and tarefa.responsavel.lower() == nome.lower()
        )
    ]

    if not resultado:
        raise HTTPException(
            status_code=404,
            detail='Nenhuma tarefa encontrada para esse responsavel'
        )

    return resultado


@router.get(
    '/',
    response_model=list[TarefaSaida],
    summary='Lista tarefas com filtros'
)
def listar(
    status: Annotated[
        Optional[StatusEnum],
        Query(description='Filtrar por status')
    ] = None,
    prioridade: Annotated[
        Optional[PrioridadeEnum],
        Query(description='Filtrar por prioridade')
    ] = None,
    responsavel: Annotated[
        Optional[str],
        Query(description='Filtrar por responsavel')
    ] = None,
    limite: Annotated[
        int,
        Query(ge=1, le=100, description='Quantidade por pagina')
    ] = 20,
    pagina: Annotated[
        int,
        Query(ge=1, description='Numero da pagina')
    ] = 1
):
    resultado = banco

    if status:
        resultado = [
            tarefa
            for tarefa in resultado
            if tarefa.status == status
        ]

    if prioridade:
        resultado = [
            tarefa
            for tarefa in resultado
            if tarefa.prioridade == prioridade
        ]

    if responsavel:
        resultado = [
            tarefa
            for tarefa in resultado
            if responsavel.lower() in (tarefa.responsavel or '').lower()
        ]

    inicio = (pagina - 1) * limite
    fim = inicio + limite

    return resultado[inicio:fim]


@router.get(
    '/{tarefa_id}',
    response_model=TarefaSaida,
    summary='Busca uma tarefa pelo ID'
)
def buscar(
    tarefa_id: Annotated[
        int,
        Path(ge=1, description='ID da tarefa')
    ]
):
    for tarefa in banco:
        if tarefa.id == tarefa_id:
            return tarefa

    raise HTTPException(
        status_code=404,
        detail='Tarefa nao encontrada'
    )


@router.post(
    '/',
    response_model=TarefaSaida,
    status_code=201,
    summary='Cria uma nova tarefa'
)
def criar(dados: TarefaEntrada):
    global proximo_id

    nova = TarefaSaida(
        id=proximo_id,
        **dados.model_dump()
    )

    banco.append(nova)
    proximo_id += 1

    return nova


@router.put(
    '/{tarefa_id}',
    response_model=TarefaSaida,
    summary='Substitui uma tarefa inteira'
)
def atualizar(
    tarefa_id: Annotated[
        int,
        Path(ge=1, description='ID da tarefa')
    ],
    dados: TarefaEntrada
):
    for indice, tarefa in enumerate(banco):
        if tarefa.id == tarefa_id:
            criado_em_original = tarefa.criado_em

            banco[indice] = TarefaSaida(
                id=tarefa_id,
                criado_em=criado_em_original,
                **dados.model_dump()
            )

            return banco[indice]

    raise HTTPException(
        status_code=404,
        detail='Tarefa nao encontrada'
    )


@router.patch(
    '/{tarefa_id}/status',
    response_model=TarefaSaida,
    summary='Atualiza apenas o status da tarefa'
)
def atualizar_status(
    tarefa_id: Annotated[
        int,
        Path(ge=1, description='ID da tarefa')
    ],
    dados: StatusAtualizacao
):
    for indice, tarefa in enumerate(banco):
        if tarefa.id == tarefa_id:
            if (
                tarefa.status == StatusEnum.cancelada
                and dados.status != StatusEnum.cancelada
            ):
                raise HTTPException(
                    status_code=400,
                    detail='Uma tarefa cancelada nao pode mudar de status'
                )

            dados_atuais = tarefa.model_dump()
            dados_atuais['status'] = dados.status

            banco[indice] = TarefaSaida(**dados_atuais)

            return banco[indice]

    raise HTTPException(
        status_code=404,
        detail='Tarefa nao encontrada'
    )


@router.patch(
    '/{tarefa_id}',
    response_model=TarefaSaida,
    summary='Atualiza campos especificos'
)
def atualizar_parcial(
    tarefa_id: Annotated[
        int,
        Path(ge=1, description='ID da tarefa')
    ],
    dados: TarefaParcial
):
    for indice, tarefa in enumerate(banco):
        if tarefa.id == tarefa_id:
            dados_atuais = tarefa.model_dump()
            novos_dados = dados.model_dump(exclude_none=True)

            if (
                tarefa.status == StatusEnum.cancelada
                and 'status' in novos_dados
                and novos_dados['status'] != StatusEnum.cancelada
            ):
                raise HTTPException(
                    status_code=400,
                    detail='Uma tarefa cancelada nao pode mudar de status'
                )

            dados_atuais.update(novos_dados)
            banco[indice] = TarefaSaida(**dados_atuais)

            return banco[indice]

    raise HTTPException(
        status_code=404,
        detail='Tarefa nao encontrada'
    )


@router.delete(
    '/{tarefa_id}',
    status_code=204,
    summary='Remove uma tarefa'
)
def deletar(
    tarefa_id: Annotated[
        int,
        Path(ge=1, description='ID da tarefa')
    ]
):
    for indice, tarefa in enumerate(banco):
        if tarefa.id == tarefa_id:
            banco.pop(indice)
            return Response(status_code=204)

    raise HTTPException(
        status_code=404,
        detail='Tarefa nao encontrada'
    )
