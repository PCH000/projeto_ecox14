import logging

log = logging.getLogger(__name__)


def conferir_chaves(esquerda, direita, col_esq, col_dir):
    esq = set(esquerda[col_esq].dropna())
    dir_ = set(direita[col_dir].dropna())

    so_esquerda = esq - dir_
    so_direita = dir_ - esq
    nos_dois = esq & dir_

    log.info("chaves so em %s: %d", col_esq, len(so_esquerda))
    log.info("chaves so em %s: %d", col_dir, len(so_direita))
    log.info("chaves nos dois: %d", len(nos_dois))

    if so_esquerda:
        log.debug("exemplos so na esquerda: %s", sorted(so_esquerda)[:5])
    if so_direita:
        log.debug("exemplos so na direita: %s", sorted(so_direita)[:5])

    return so_esquerda, so_direita, nos_dois


def juntar(esquerda, direita, col_esq, col_dir, relacao="many_to_one"):
    return esquerda.merge(
        direita,
        left_on=col_esq,
        right_on=col_dir,
        how="left",
        validate=relacao,
    )


def validar(esquerda, resultado, coluna_da_direita):
    """Confere a conta e devolve as linhas que nao casaram."""
    sem_par = resultado[coluna_da_direita].isna()

    log.info("linhas na esquerda : %d", len(esquerda))
    log.info("linhas no resultado: %d", len(resultado))
    log.warning("sem par            : %d", int(sem_par.sum()))

    if len(resultado) < len(esquerda):
        log.warning("resultado perdeu linhas. Juncao do tipo errado?")
    elif len(resultado) > len(esquerda):
        log.warning("resultado ganhou linhas. A chave repete na direita.")

    return resultado[sem_par]