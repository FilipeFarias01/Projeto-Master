const BASE = 'http://127.0.0.1:8000';

const listaEl = document.querySelector('#lista');
const loadingEl = document.querySelector('#loading');
const erroEl = document.querySelector('#erro');
const resumoEl = document.querySelector('#resumo');
const modalEl = document.querySelector('#modal-tarefa');
const formEl = document.querySelector('#form-tarefa');

const mostrarLoading = () => {
    loadingEl.classList.remove('hidden');
    erroEl.classList.add('hidden');
    listaEl.classList.add('hidden');
};

const mostrarErro = (mensagem) => {
    loadingEl.classList.add('hidden');
    erroEl.classList.remove('hidden');
    listaEl.classList.add('hidden');
    erroEl.textContent = mensagem;
};

const mostrarLista = () => {
    loadingEl.classList.add('hidden');
    erroEl.classList.add('hidden');
    listaEl.classList.remove('hidden');
};

const renderizar = (tarefas) => {
    if (tarefas.length === 0) {
        listaEl.innerHTML = `
            <div class="sem-resultados">
                Nenhuma tarefa encontrada.
            </div>
        `;
        mostrarLista();
        return;
    }

    listaEl.innerHTML = tarefas.map(tarefa => `
        <article
            class="card-tarefa ${tarefa.prioridade}"
            data-id="${tarefa.id}"
        >
            <p class="card-titulo">
                ${tarefa.titulo}
            </p>

            ${
                tarefa.descricao
                ? `<p class="card-desc">${tarefa.descricao}</p>`
                : ''
            }

            <div class="card-meta">
                <span class="badge badge-${tarefa.status}">
                    ${tarefa.status.replace('_', ' ')}
                </span>

                <span class="badge">
                    ${tarefa.prioridade}
                </span>

                ${
                    tarefa.responsavel
                    ? `<span>👤 ${tarefa.responsavel}</span>`
                    : ''
                }

                ${
                    tarefa.prazo
                    ? `<span>📅 Prazo: ${tarefa.prazo}</span>`
                    : ''
                }

                ${
                    tarefa.criado_em
                    ? `<span>Criado: ${tarefa.criado_em}</span>`
                    : ''
                }
            </div>

            ${
                tarefa.tags && tarefa.tags.length > 0
                ? `
                    <div class="tags">
                        ${tarefa.tags.map(tag => `
                            <span class="badge badge-tag">
                                ${tag}
                            </span>
                        `).join('')}
                    </div>
                `
                : ''
            }

            <div class="card-acoes">
                ${
                    tarefa.status !== 'concluida'
                    && tarefa.status !== 'cancelada'
                    ? `
                        <button
                            class="btn-concluir"
                            data-id="${tarefa.id}"
                        >
                            Concluir
                        </button>
                    `
                    : ''
                }

                <button
                    class="btn-deletar"
                    data-id="${tarefa.id}"
                >
                    Remover
                </button>
            </div>
        </article>
    `).join('');

    mostrarLista();
};

const atualizarResumo = async () => {
    try {
        const resposta = await fetch(
            `${BASE}/tarefas/estatisticas`
        );

        if (!resposta.ok) {
            throw new Error(
                `Erro ${resposta.status}`
            );
        }

        const dados = await resposta.json();

        resumoEl.textContent =
            `Total: ${dados.total}`
            + ` | Pendentes: ${dados.por_status.pendente}`
            + ` | Em andamento: ${dados.por_status.em_andamento}`
            + ` | Concluídas: ${dados.por_status.concluida}`
            + ` | Canceladas: ${dados.por_status.cancelada}`;
    } catch (erro) {
        resumoEl.textContent = '';
    }
};

const listar = async () => {
    mostrarLoading();

    const status = document.querySelector(
        '#filtro-status'
    ).value;

    const prioridade = document.querySelector(
        '#filtro-prioridade'
    ).value;

    const responsavel = document.querySelector(
        '#filtro-responsavel'
    ).value.trim();

    const params = new URLSearchParams();

    if (status) {
        params.append('status', status);
    }

    if (prioridade) {
        params.append('prioridade', prioridade);
    }

    if (responsavel) {
        params.append('responsavel', responsavel);
    }

    try {
        const resposta = await fetch(
            `${BASE}/tarefas?${params}`
        );

        if (!resposta.ok) {
            throw new Error(
                `Erro ${resposta.status}`
            );
        }

        const tarefas = await resposta.json();

        renderizar(tarefas);
        await atualizarResumo();

    } catch (erro) {
        mostrarErro(erro.message);
    }
};

formEl.addEventListener(
    'submit',
    async (evento) => {
        evento.preventDefault();

        const tagsTexto = document.querySelector(
            '#tags'
        ).value;

        const tags = tagsTexto
            .split(',')
            .map(tag => tag.trim())
            .filter(tag => tag !== '');

        const dados = {
            titulo: document.querySelector(
                '#titulo'
            ).value,

            descricao: document.querySelector(
                '#descricao'
            ).value || null,

            responsavel: document.querySelector(
                '#responsavel'
            ).value || null,

            prioridade: document.querySelector(
                '#prioridade'
            ).value,

            prazo: document.querySelector(
                '#prazo'
            ).value || null,

            tags: tags
        };

        try {
            const resposta = await fetch(
                `${BASE}/tarefas`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type':
                            'application/json'
                    },

                    body: JSON.stringify(dados)
                }
            );

            if (!resposta.ok) {
                const erro = await resposta.json();

                throw new Error(
                    typeof erro.detail === 'string'
                    ? erro.detail
                    : 'Erro ao criar tarefa'
                );
            }

            modalEl.close();
            formEl.reset();
            await listar();

        } catch (erro) {
            alert(
                `Erro: ${erro.message}`
            );
        }
    }
);

listaEl.addEventListener(
    'click',
    async (evento) => {
        const id = evento.target.dataset.id;

        if (!id) {
            return;
        }

        if (
            evento.target.classList.contains(
                'btn-concluir'
            )
        ) {
            try {
                const resposta = await fetch(
                    `${BASE}/tarefas/${id}/status`,
                    {
                        method: 'PATCH',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body: JSON.stringify(
                            {
                                status: 'concluida'
                            }
                        )
                    }
                );

                if (!resposta.ok) {
                    const erro =
                        await resposta.json();

                    throw new Error(
                        erro.detail
                        || 'Erro ao concluir tarefa'
                    );
                }

                await listar();

            } catch (erro) {
                alert(
                    `Erro: ${erro.message}`
                );
            }
        }

        if (
            evento.target.classList.contains(
                'btn-deletar'
            )
        ) {
            const confirmar = confirm(
                'Remover esta tarefa?'
            );

            if (!confirmar) {
                return;
            }

            try {
                const resposta = await fetch(
                    `${BASE}/tarefas/${id}`,
                    {
                        method: 'DELETE'
                    }
                );

                if (!resposta.ok) {
                    const erro =
                        await resposta.json();

                    throw new Error(
                        erro.detail
                        || 'Erro ao remover tarefa'
                    );
                }

                await listar();

            } catch (erro) {
                alert(
                    `Erro: ${erro.message}`
                );
            }
        }
    }
);

document.querySelector(
    '#btn-nova'
).addEventListener(
    'click',
    () => {
        formEl.reset();
        modalEl.showModal();
    }
);

document.querySelector(
    '#btn-cancelar'
).addEventListener(
    'click',
    () => {
        modalEl.close();
    }
);

document.querySelector(
    '#btn-filtrar'
).addEventListener(
    'click',
    listar
);

document.querySelector(
    '#filtro-responsavel'
).addEventListener(
    'keydown',
    evento => {
        if (evento.key === 'Enter') {
            listar();
        }
    }
);

listar();
