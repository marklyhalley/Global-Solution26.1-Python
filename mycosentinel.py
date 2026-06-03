# MycoSentinel — Sistema de monitoramento e simulação de redes miceliais
# para ambientes extremos (Terra, Lua e Marte). Coordena análise de solo,
# recomendação de fungos, simulação de regeneração e geração de relatórios.

from colorama import init, Fore, Back, Style
import random
import os
import datetime
import json

# ── Estado global da missão ──────────────────────────────────────────────────
# Estas variáveis representam o contexto persistente da sessão.
# São modificadas ao longo da execução e consultadas por múltiplas funções.

ambiente_atual   = None   # Planeta/ambiente ativo; None indica que nenhum foi selecionado
solo_analisado   = {}     # Últimos parâmetros coletados pelos sensores de solo
fase_atual       = 0      # Progresso da simulação: 0 = não iniciada; 1–4 = fases concluídas
saude_micelial   = 100    # Índice de saúde da rede micelial; decresce com eventos adversos

init(autoreset=True)      # Inicializa o Colorama com reset automático após cada impressão

# ── Paleta semântica de cores ────────────────────────────────────────────────
# Cada constante agrupa cor + brilho para um nível de mensagem específico,
# garantindo consistência visual em toda a interface de texto.
TITULO   = Fore.CYAN    + Style.BRIGHT
SUCESSO  = Fore.GREEN   + Style.BRIGHT
ALERTA   = Fore.YELLOW  + Style.BRIGHT
ERRO     = Fore.RED     + Style.BRIGHT
INFO     = Fore.BLUE
DESTAQUE = Fore.MAGENTA + Style.BRIGHT


# Simula limpeza de tela imprimindo linhas em branco, compatível com
# ambientes que não suportam os comandos 'cls' ou 'clear'.
def limpar_tela():
        print("\n" * 100)

def pausar():
    input("\n  [ ENTER para continuar... ]")


# Exibe o cabeçalho padrão de cada tela, consolidando o estado atual da missão
# (ambiente, fase e saúde micelial) para contextualizar o usuário a cada ação.
def cabecalho(titulo):
    limpar_tela()

    print(TITULO + "=" * 55)
    print(TITULO + f"  MycoSentinel — {titulo}")
    print(TITULO + "=" * 55)

    print(INFO + f"  Ambiente: {ambiente_atual or 'Não selecionado'}")

    if fase_atual == 0:
        print(INFO + "  Fase: Não iniciada")
    else:
        print(INFO + f"  Fase: {fase_atual}")

    # A cor do indicador muda conforme o nível de risco:
    # verde (≥70%), amarelo (40–69%) e vermelho (<40%).
    if saude_micelial >= 70:
        cor_saude = SUCESSO
    elif saude_micelial >= 40:
        cor_saude = ALERTA
    else:
        cor_saude = ERRO

    print(cor_saude + f"  Saúde: {saude_micelial}%")

    print(TITULO + "=" * 55)
    print()


# Lê e valida uma opção numérica do usuário dentro do intervalo [0, maximo].
# Repete a solicitação até que uma entrada válida seja fornecida.
def ler_opcao(maximo):
    while True:
        try:
            op = int(input("  Opção: "))
            if 0 <= op <= maximo:
                return op
            print(f"  [!] Digite entre 0 e {maximo}.")
        except ValueError:
            print("  [!] Apenas números.")


# Persiste eventos relevantes da sessão no arquivo missao_log.txt.
# Cada entrada é prefixada com data e hora para rastreabilidade da missão.
def registrar_log(mensagem):
    try:
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        with open("missao_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{agora}] {mensagem}\n")
    except Exception as e:
        print(f"  [!] Erro ao salvar log: {e}")



# Permite ao usuário definir o ambiente planetário da missão.
# O ambiente influencia diretamente a compatibilidade dos fungos recomendados.
def selecionar_ambiente():
    global ambiente_atual
    cabecalho("Selecionar Ambiente")
    print("  1. Terra")
    print("  2. Lua")
    print("  3. Marte")
    print()
    op = ler_opcao(3)

    if op == 0:
        return
    elif op == 1:
        ambiente_atual = "Terra"
        print("\n  Ambiente Terra selecionado.")
        print("  Gravidade normal, atmosfera presente, solo úmido.")
    elif op == 2:
        ambiente_atual = "Lua"
        print("\n  Ambiente Lua selecionado.")
        print("  Sem atmosfera, radiação alta, temperatura extrema.")
    elif op == 3:
        ambiente_atual = "Marte"
        print("\n  Ambiente Marte selecionado.")
        print("  Atmosfera fina, solo perclórico, frio intenso.")

    registrar_log(f"Ambiente selecionado: {ambiente_atual}")


# Simula a coleta de dados dos sensores de solo e classifica cada parâmetro.
# Os valores são gerados aleatoriamente para reproduzir variações reais de campo.
# Requer que um ambiente já tenha sido selecionado.
def analisar_solo():
    global solo_analisado
    cabecalho("Analisar Solo")

    if ambiente_atual is None:
        print("  [!] Selecione um ambiente antes de analisar o solo.")
        return

    print("  Coletando dados dos sensores...\n")

    # Cada parâmetro é gerado dentro de uma faixa realista para o contexto da missão.
    solo_analisado = {
        "pH"        : round(random.uniform(3.0, 9.0), 1),
        "umidade"   : round(random.uniform(0, 100), 1),
        "nitrogenio": round(random.uniform(0, 100), 1),
        "toxicidade": round(random.uniform(0.0, 5.0), 2),
        "temperatura": round(random.uniform(-60, 40), 1)
    }

    print(f"  {'Parâmetro':<14} {'Valor':<10} {'Status'}")
    print("  " + "-" * 38)

    for parametro, valor in solo_analisado.items():

        # Faixas de pH: acidez ou alcalinidade extremas são incompatíveis
        # com o desenvolvimento micelial e indicam solo inviável.
        if parametro == "pH":
            if valor < 4.0 or valor > 8.5:
                status = "CRÍTICO"
            elif valor < 5.5 or valor > 7.5:
                status = "ATENÇÃO"
            else:
                status = "NORMAL"

        elif parametro == "umidade":
            if valor < 10:
                status = "CRÍTICO"
            elif valor < 30:
                status = "ATENÇÃO"
            else:
                status = "NORMAL"

        elif parametro == "nitrogenio":
            if valor < 15:
                status = "CRÍTICO"
            elif valor < 40:
                status = "ATENÇÃO"
            else:
                status = "NORMAL"

        # Toxicidade acima de 3.5 indica contaminantes em nível letal para fungos.
        elif parametro == "toxicidade":
            if valor > 3.5:
                status = "CRÍTICO"
            elif valor > 2.0:
                status = "ATENÇÃO"
            else:
                status = "NORMAL"

        elif parametro == "temperatura":
            if valor < -20 or valor > 35:
                status = "CRÍTICO"
            elif valor < 5 or valor > 28:
                status = "ATENÇÃO"
            else:
                status = "NORMAL"

        else:
            status = "DESCONHECIDO"

        if status == "CRÍTICO":
            cor = ERRO
        elif status == "ATENÇÃO":
            cor = ALERTA
        else:
            cor = SUCESSO

        print(f"  {parametro:<14} {str(valor):<10} {cor}{status}")

    registrar_log(f"Solo analisado: {solo_analisado}")


# Carrega a base de espécies fúngicas a partir do arquivo fungos.json.
# O JSON estrutura cada fungo com parâmetros de compatibilidade ambiental,
# utilizados pelo sistema de recomendação para o cruzamento com os dados do solo.
def carregar_fungos_json():
    try:
        with open("fungos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("  [!] Arquivo fungos.json não encontrado.")
        return []
    except json.JSONDecodeError:
        print("  [!] Erro ao ler fungos.json. Verifique o formato do arquivo.")
        return []

# Cruza os dados do solo com o banco de espécies para sugerir fungos compatíveis.
# A recomendação considera fase da simulação, pH, umidade, toxicidade,
# temperatura e ambiente planetário simultaneamente.
def recomendar_fungos():
    cabecalho("Recomendar Fungos")

    if not solo_analisado:
        print("  [!] Analise o solo antes de recomendar fungos.")
        return

    if ambiente_atual is None:
        print("  [!] Selecione um ambiente antes de recomendar fungos.")
        return

    fungos = carregar_fungos_json()
    if not fungos:
        return

    ph          = solo_analisado["pH"]
    umidade     = solo_analisado["umidade"]
    toxicidade  = solo_analisado["toxicidade"]
    temperatura = solo_analisado["temperatura"]

    print("  Cruzando dados do solo com banco de fungos...\n")

    # A recomendação é sempre orientada à próxima fase a ser executada.
    # Ao atingir a fase 4 (máxima), o sistema mantém os fungos da fase final.
    fase_alvo = fase_atual + 1 if fase_atual < 4 else 4

    if fase_atual == 0:
        print("  Simulação não iniciada — exibindo fungos da Fase 1.\n")
    elif fase_atual == 4:
        print("  Simulação concluída — exibindo fungos da Fase 4.\n")
    else:
        print(f"  Fase {fase_atual} concluída — exibindo fungos da Fase {fase_alvo}.\n")

    recomendados = []

    # Cada fungo é avaliado contra seis critérios de compatibilidade.
    # Somente espécies que satisfazem todos os critérios são incluídas na lista.
    for fungo in fungos:
        compativel_fase        = fungo["fase"]            == fase_alvo
        compativel_ph          = fungo["ph_min"]          <= ph          <= fungo["ph_max"]
        compativel_umidade     = umidade                  >= fungo["umidade_min"]
        compativel_toxicidade  = toxicidade               <= fungo["toxicidade_max"]
        compativel_temperatura = fungo["temperatura_min"] <= temperatura <= fungo["temperatura_max"]
        compativel_ambiente    = ambiente_atual           in fungo["ambientes"]

        if compativel_fase and compativel_ph and compativel_umidade and compativel_toxicidade and compativel_temperatura and compativel_ambiente:
            recomendados.append(fungo)

    if not recomendados:
        print("  Nenhum fungo compatível com as condições atuais.")
        print("  Reavalie os parâmetros do solo ou o ambiente selecionado.")
        registrar_log("Recomendação: nenhum fungo compatível encontrado.")
        return

    recomendados.sort(key=lambda f: f["fase"])

    print(f"  {len(recomendados)} fungo(s) compatível(is) encontrado(s):\n")
    print(f"  {'#':<4} {'Nome':<30} {'Fase':<6} {'Função'}")
    print("  " + "-" * 65)

    for i, fungo in enumerate(recomendados, 1):
        print(f"  {i:<4} {fungo['nome']:<30} {fungo['fase']:<6} {fungo['funcao']}")

    print()
    print("  Digite o número para ver detalhes ou 0 para voltar:")
    try:
        escolha = int(input("  Opção: "))
        if 1 <= escolha <= len(recomendados):
            f = recomendados[escolha - 1]
            print()
            print(f"  Nome       : {f['nome']}")
            print(f"  Fase       : {f['fase']} — {f['funcao']}")
            print(f"  Descrição  : {f['descricao']}")
            print(f"  pH ideal   : {f['ph_min']} a {f['ph_max']}")
            print(f"  Temperatura: {f['temperatura_min']}°C a {f['temperatura_max']}°C")
            print(f"  Ambientes  : {', '.join(f['ambientes'])}")
    except ValueError:
        pass

    nomes = [f["nome"] for f in recomendados]
    registrar_log(f"Fungos recomendados para {ambiente_atual}: {', '.join(nomes)}")


# Executa as fases de regeneração do solo em sequência, uma por chamada.
# Cada fase é composta por 5 ciclos com eventos aleatórios que impactam
# a saúde micelial, simulando riscos reais de campo.
def simular_regeneracao():
    global fase_atual, saude_micelial
    cabecalho("Simular Regeneração")

    if not solo_analisado:
        print("  [!] Analise o solo antes de simular.")
        return

    # As quatro fases representam etapas progressivas de restauração ecológica.
    fases = [
        "Desintoxicação do solo",
        "Estruturação micelial",
        "Nutrição e regeneração",
        "Proteção e estabilidade"
    ]

    # Ao concluir todas as fases, o usuário pode reiniciar a simulação do zero.
    if fase_atual == 4:
        print("  Todas as fases já foram concluídas!")
        print(f"  Saúde final da missão: {saude_micelial}%")
        print()
        print("  1. Reiniciar simulação")
        print("  0. Voltar")
        print()
        op = ler_opcao(1)
        if op == 1:
            fase_atual     = 0
            saude_micelial = 100
            print("\n  Simulação reiniciada. Saúde restaurada para 100%.")
            registrar_log("Simulação reiniciada pelo usuário.")
        return

    proxima = fase_atual + 1
    nome_fase = fases[proxima - 1]

    print(f"  Fase atual concluída : {fase_atual if fase_atual > 0 else 'Nenhuma'}")
    print(f"  Próxima fase         : {proxima} — {nome_fase}")
    print()
    print("  1. Executar esta fase")
    print("  0. Voltar ao menu")
    print()
    op = ler_opcao(1)

    if op == 0:
        return

    print(f"\n  FASE {proxima}: {nome_fase}")
    print("  " + "-" * 38)

    for ciclo in range(1, 6):
        # Distribuição de probabilidade dos eventos por ciclo:
        # 20% contaminação (−10 pts), 20% variação térmica (−5 pts), 60% estável.
        evento = random.randint(1, 10)

        if evento <= 2:
            print(ERRO + f"  Ciclo {ciclo}: ALERTA — Contaminação detectada!")
            saude_micelial -= 10
            registrar_log(f"ALERTA | Fase {proxima} | Ciclo {ciclo} | Contaminação detectada.")
        elif evento <= 4:
            print(ALERTA + f"  Ciclo {ciclo}: ATENÇÃO — Variação de temperatura.")
            saude_micelial -= 5
            registrar_log(f"ATENÇÃO | Fase {proxima} | Ciclo {ciclo} | Variação de temperatura.")
        else:
            print(SUCESSO + f"  Ciclo {ciclo}: OK — Rede micelial estável.")
            registrar_log(f"INFO | Fase {proxima} | Ciclo {ciclo} | Estável.")

        # Encerra a fase imediatamente se a saúde atingir zero,
        # bloqueando o avanço para as fases seguintes.
        if saude_micelial <= 0:
            saude_micelial = 0
            print("\n  [!] Saúde micelial zerada. Simulação encerrada.")
            registrar_log(f"Simulação encerrada na fase {proxima}. Saúde: 0%")
            return

    fase_atual = proxima
    print(f"\n  Fase {fase_atual} concluída! Saúde atual: {saude_micelial}%")
    registrar_log(f"Fase {fase_atual} concluída. Saúde: {saude_micelial}%")

    if fase_atual == 4:
        print("  Simulação completa! Todas as fases concluídas.")
        registrar_log(f"Simulação concluída. Saúde final: {saude_micelial}%")


# Coleta e analisa sinais bioelétricos da rede micelial.
# Os valores simulam leituras de sensores distribuídos pela estrutura fúngica,
# permitindo diagnosticar a atividade e integridade do micélio em tempo real.
def monitor_bioeletrico():
    cabecalho("Monitor Bioelétrico")

    print("  Gerando leituras biolétricas da rede micelial...\n")

    # 10 leituras independentes representam pontos distintos da rede micelial.
    sinais = [round(random.uniform(0.5, 5.0), 2) for _ in range(10)]
    media  = round(sum(sinais) / len(sinais), 2)
    minimo = min(sinais)
    maximo = max(sinais)

    print(f"  Sinais coletados : {sinais}")
    print(f"  Média            : {media}")
    print(f"  Mínimo / Máximo  : {minimo} / {maximo}\n")

    print("  Diagnóstico por leitura:\n")

    # Cada leitura é classificada individualmente para identificar pontos críticos
    # na rede, mesmo quando a média geral se mantém dentro do intervalo normal.
    for i, sinal in enumerate(sinais):
        if sinal < 1.0:
            status = ERRO + "CRÍTICO — Possível morte micelial"
        elif sinal < 2.0:
            status = ALERTA + "ATENÇÃO — Atividade baixa"
        elif sinal > 4.5:
            status = DESTAQUE + "ALERTA — Crescimento acelerado"
        else:
            status = SUCESSO + "NORMAL"

        print(f"  Leitura {i+1:02d}: {sinal}  →  {status}")

    # O diagnóstico consolidado é baseado na média das leituras,
    # refletindo o estado predominante da rede como um geral.
    print()
    if media < 1.5:
        print("  Conclusão: Rede micelial em colapso.")
    elif media < 2.5:
        print("  Conclusão: Rede micelial debilitada.")
    elif media > 4.0:
        print("  Conclusão: Crescimento anormal detectado.")
    else:
        print("  Conclusão: Rede micelial saudável.")

    registrar_log(f"Monitor bioelétrico — média: {media}, min: {minimo}, max: {maximo}")




# Exibe o histórico de eventos registrados em missao_log.txt.
# Suporta filtro por palavra-chave para facilitar a auditoria de ocorrências específicas.
def consultar_log():
    cabecalho("Consultar Log da Missão")

    try:
        with open("missao_log.txt", "r", encoding="utf-8") as f:
            linhas = f.readlines()

        if not linhas:
            print("  Log vazio.")
            return

        print("  Filtrar por: (deixe em branco para ver tudo)")
        filtro = input("  Palavra-chave: ").strip().lower()
        print()

        encontrou = False
        for linha in linhas:
            if filtro == "" or filtro in linha.lower():
                print(" ", linha.strip())
                encontrou = True

        if not encontrou:
            print("  Nenhuma entrada encontrada para esse filtro.")

    except FileNotFoundError:
        print("  [!] Nenhum log encontrado ainda.")




# Gerencia o banco de espécies cadastradas manualmente pelo usuário.
# Os fungos são armazenados em fungos.txt, em formato textual simples com campos
# separados por pipe (|), servindo como registro complementar ao fungos.json.
def banco_de_fungos():
    cabecalho("Banco de Fungos")
    print("  1. Listar fungos cadastrados")
    print("  2. Cadastrar novo fungo")
    print("  0. Voltar")
    print()
    op = ler_opcao(2)

    if op == 1:
        try:
            with open("fungos.txt", "r", encoding="utf-8") as f:
                linhas = f.readlines()
            if not linhas:
                print(ALERTA + "  [!] Nenhum fungo cadastrado no banco.")
                print(INFO + "  Use a opção 2 para cadastrar um novo fungo.")
            else:
                for linha in linhas:
                    print(" ", linha.strip())
        except FileNotFoundError:
            print(ALERTA + "  [!] Nenhum fungo cadastrado no banco.")
            print(INFO + "  Use a opção 2 para cadastrar um novo fungo.")

    elif op == 2:
        nome      = input("  Nome do fungo  : ").strip()
        fase      = input("  Fase (1 a 4)   : ").strip()
        local     = input("  Ambiente       : ").strip()
        descricao = input("  Descrição      : ").strip()

        # Cada entrada é gravada em uma linha com campos separados por pipe,
        # formato suficiente para exibição e auditoria manual do banco.
        try:
            with open("fungos.txt", "a", encoding="utf-8") as f:
                f.write(f"{nome} | Fase {fase} | {local} | {descricao}\n")
            print(f"\n  Fungo '{nome}' cadastrado com sucesso!")
            registrar_log(f"Fungo cadastrado: {nome}")
        except Exception as e:
            print(f"  [!] Erro ao salvar fungo: {e}")




# Consolida os dados da sessão em um arquivo de relatório com timestamp no nome.
# O arquivo é salvo localmente e exibido no terminal ao término da geração.
def gerar_relatorio():
    cabecalho("Gerar Relatório")

    agora    = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    # O timestamp no nome do arquivo evita sobrescrita entre sessões distintas.
    nome_arq = f"relatorio_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}.txt"

    linhas = []
    linhas.append("=" * 45)
    linhas.append("  RELATÓRIO DE MISSÃO — MycoSentinel")
    linhas.append("=" * 45)
    linhas.append(f"  Data       : {agora}")
    linhas.append(f"  Ambiente   : {ambiente_atual or 'Não definido'}")
    linhas.append(f"  Fase final : {fase_atual or 'Nenhuma'}")
    linhas.append(f"  Saúde final: {saude_micelial}%")
    linhas.append("=" * 45)
    linhas.append("  DADOS DO SOLO")
    linhas.append("-" * 45)

    if solo_analisado:
        for parametro, valor in solo_analisado.items():
            linhas.append(f"  {parametro:<14}: {valor}")
    else:
        linhas.append("  Solo não analisado.")

    linhas.append("=" * 45)

    # Classificação final baseada na saúde micelial acumulada ao longo da simulação.
    if saude_micelial >= 75:
        linhas.append("  Status geral: MISSÃO BEM-SUCEDIDA")
    elif saude_micelial >= 40:
        linhas.append("  Status geral: MISSÃO PARCIALMENTE CONCLUÍDA")
    else:
        linhas.append("  Status geral: MISSÃO CRÍTICA — REVISAR PROTOCOLO")

    linhas.append("=" * 45)

    try:
        with open(nome_arq, "w", encoding="utf-8") as f:
            for linha in linhas:
                f.write(linha + "\n")
        for linha in linhas:
            print(linha)
        print(f"\n  Relatório salvo em: {nome_arq}")
        registrar_log(f"Relatório gerado: {nome_arq}")
    except Exception as e:
        print(f"  [!] Erro ao salvar relatório: {e}")



# Loop principal do sistema. Exibe o menu de navegação e despacha cada
# opção para sua respectiva função até que o usuário escolha sair.
def menu():
    while True:
        print(SUCESSO + "  1. Selecionar ambiente")
        print(INFO + "     Escolha entre Terra, Lua ou Marte.")
        print()

        print(SUCESSO + "  2. Analisar solo")
        print(INFO + "     Lê sensores e classifica cada parâmetro.")
        print()

        print(SUCESSO + "  3. Recomendar fungos")
        print(INFO + "     A IA sugere espécies com base no solo.")
        print()

        print(SUCESSO + "  4. Simular regeneração")
        print(INFO + "     Executa as 4 fases com eventos aleatórios.")
        print()

        print(SUCESSO + "  5. Monitor bioelétrico")
        print(INFO + "     Analisa sinais da rede micelial.")
        print()

        print(SUCESSO + "  6. Consultar log")
        print(INFO + "     Exibe o histórico de eventos da missão.")
        print()

        print(SUCESSO + "  7. Banco de fungos")
        print(INFO + "     Lista e cadastra espécies fúngicas.")
        print()

        print(SUCESSO + "  8. Gerar relatório")
        print(INFO + "     Salva um resumo completo da missão.")
        print()

        print(ERRO + "  0. Sair")

        op = ler_opcao(8)

        if   op == 1: selecionar_ambiente()
        elif op == 2: analisar_solo()
        elif op == 3: recomendar_fungos()
        elif op == 4: simular_regeneracao()
        elif op == 5: monitor_bioeletrico()
        elif op == 6: consultar_log()
        elif op == 7: banco_de_fungos()
        elif op == 8: gerar_relatorio()
        elif op == 0:
            print("\n  Encerrando MycoSentinel...\n")
            break

        pausar()



menu()