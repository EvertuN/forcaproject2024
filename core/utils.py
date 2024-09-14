from core.models import Tema


def gerar_relatorio(tema):
    if not isinstance(tema, Tema):
        raise ValueError("O parâmetro deve ser uma instância de Tema")

    dados = {
        'nome': tema.nome,
        'palavras': tema.palavra_set.all(),
    }

    return dados