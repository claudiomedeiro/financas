#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""O script mantém um fluxo de caixa de finanças pessoais, bem como as funções
de interação com ele, como algumas das funcionalidades abaixo relacionadas:

- Inserir novas ocorrências
- Alterar ocorrências
- Visualizar extrato
- Definir saldo de contas

TODO: Repensar questão de chamada de método de montagem de página de maneira 
encadeada, porque muitas instâncias consomem muita memória.
"""

from os import system
from time import sleep
from datetime import datetime
from sqlite3 import connect, Error
from math import sqrt
from sys import exit

str_banco = "financas.db"
str_separador = ";"
dic_paginas = {}
dic_larguras = {"SubConta": 0, "Oque": 0, "Valor": 0, "Detalhe": 0}

# As listas de apenas 01 elemento convertidas em tuplas, acrescentam uma 
# vírgula que não é tolerada no comando 'SELECT', então fiz uma brincadeira 
# ao concatenar uma 'data' inválida
proporcao_aurea = "proporcao_aurea {}".format((1+sqrt(5))/2)

# TODO: Colocar no arquivo de configurações e pensar funcionalidade para 
# alterar pelo usuário. Pensar também em não permitir a definição do mínimo 
# menor que a maior quantidade ṕara um dia/situação
int_ocorrencias_por_pagina = 10


def monta_paginas_extrato():
    """TODO: Escrever arrazoado sobre o método
    """
    global int_ocorrencias_por_pagina
    global dic_paginas

    str_comando  = "SELECT "
    str_comando += "    Data "
    str_comando += "    ,COUNT(1) AS 'QtdeOcorrenciasDiaSituacao' "
    str_comando += "    ,Situacao "
    str_comando += "FROM "
    str_comando += "    tb_ocorrencias "
    str_comando += "GROUP BY "
    str_comando += "    Data "
    str_comando += "    ,Situacao "
    str_comando += "ORDER BY "
    str_comando += "    Situacao "
    str_comando += "    ,Data "
    vet_quantidades = executa_consulta(str_comando)

    int_total = 0
    int_pagina = 0
    str_situacao = ""
    for vet_quantidade in vet_quantidades:
        int_total += int(vet_quantidade[1])

        # Acrescenta à mesma página
        if (int_total <= int_ocorrencias_por_pagina) and (str_situacao == vet_quantidade[2]):
            dic_paginas[int_pagina]["Situacao"] = vet_quantidade[2]
            dic_paginas[int_pagina]["Datas"].append(vet_quantidade[0])

        # Nova página
        else:
            #Reinicia variáveis de página
            int_total = int(vet_quantidade[1])
            str_situacao = vet_quantidade[2]

            int_pagina += 1
            dic_paginas[int_pagina] = {}
            dic_paginas[int_pagina]["Situacao"] = vet_quantidade[2]
            dic_paginas[int_pagina]["Datas"] = []
            dic_paginas[int_pagina]["Datas"].append(vet_quantidade[0])

    return


def formata_texto_posicoes(str_texto, int_tamanho, str_caracter_preencher, str_posicao="a"):
    """Preenche determinado número de espaços (a)ntes ou (d)epois
    """
    str_antes = ""
    str_depois = ""

    if str_posicao == "a":
        str_antes = str_caracter_preencher * (int_tamanho - len(str_texto))

    elif str_posicao == "d":
        str_depois = str_caracter_preencher * (int_tamanho - len(str_texto))

    else:
        pass

    return(str_antes + str_texto + str_depois)


def carrega_extrato(int_pagina=1):
    """
    TODO: Escrever arrazoado sobre o método
    TODO: Ajustar para apresentar primeiro o que é planejado e só depois o que é realizado
    """

    global dic_paginas
    global proporcao_aurea

    #Pega ocorrências específicas
    str_comando  = "SELECT "
    str_comando += "    Data "
    str_comando += "    ,SubConta "
    str_comando += "    ,Oque "
    str_comando += "    ,Valor "
    str_comando += "    ,Detalhe "
    str_comando += "    ,Situacao "
    str_comando += "FROM "
    str_comando += "    tb_ocorrencias "
    str_comando += "WHERE "
    str_comando += "    Data in " + str(tuple(dic_paginas[int_pagina]["Datas"]+[proporcao_aurea])) + " "
    str_comando += "    AND Situacao = '" + dic_paginas[int_pagina]["Situacao"] + "' "
    str_comando += "ORDER BY "
    str_comando += "    Data ASC "
    str_comando += "    ,SubConta ASC "
    str_comando += "    ,Valor DESC "
    vet_ocorrencias = executa_consulta(str_comando)

    for vet_ocorrencia in vet_ocorrencias:
        if len(vet_ocorrencia[1]) > dic_larguras["SubConta"]:
            dic_larguras["SubConta"] = len(vet_ocorrencia[1])

        if len(vet_ocorrencia[2]) > dic_larguras["Oque"]:
            dic_larguras["Oque"] = len(vet_ocorrencia[2])

        if len(vet_ocorrencia[3]) > len("{:10.2f}".format(float(dic_larguras["Valor"]))):
            dic_larguras["Valor"] = len(vet_ocorrencia[3])

        if len(vet_ocorrencia[4]) > dic_larguras["Detalhe"]:
            dic_larguras["Detalhe"] = len(vet_ocorrencia[4])

    # Converte ocorrências em dicionário por data
    dic_ocorrencias = {}
    for vet_ocorrencia in vet_ocorrencias:
        try:
            dic_ocorrencias[vet_ocorrencia[0]].append(vet_ocorrencia[1:])
        except:
            dic_ocorrencias[vet_ocorrencia[0]] = []
            dic_ocorrencias[vet_ocorrencia[0]].append(vet_ocorrencia[1:])

    # Consulta os saldos finais das subcontas por dia
    str_comando  = "SELECT "
    str_comando += "        tb_aux_ocorrencias_01.Data "
    str_comando += "        ,tb_aux_ocorrencias_01.SubConta "
    str_comando += "        ,SUM(tb_aux_ocorrencias_02.Valor) AS 'Valor' "
    str_comando += "FROM "
    str_comando += "    ( "
    str_comando += "    SELECT "
    str_comando += "        Data "
    str_comando += "        ,SubConta "
    str_comando += "        ,SUM(Valor) AS 'Valor' "
    str_comando += "        ,Situacao "
    str_comando += "    FROM "
    str_comando += "        tb_ocorrencias "
    str_comando += "    GROUP BY "
    str_comando += "        Data "
    str_comando += "        ,SubConta "
    str_comando += "        ,Situacao "
    str_comando += "    ) AS 'tb_aux_ocorrencias_01'  "
    str_comando += "    INNER JOIN "
    str_comando += "        ( "
    str_comando += "        SELECT "
    str_comando += "            Data "
    str_comando += "            ,SubConta "
    str_comando += "            ,SUM(Valor) AS 'Valor' "
    str_comando += "            ,Situacao "
    str_comando += "        FROM "
    str_comando += "            tb_ocorrencias "
    str_comando += "        GROUP BY "
    str_comando += "            Data "
    str_comando += "            ,SubConta "
    str_comando += "            ,Situacao "
    str_comando += "        ) AS 'tb_aux_ocorrencias_02'      "
    str_comando += "    ON "
    str_comando += "    tb_aux_ocorrencias_01.Data >= tb_aux_ocorrencias_02.Data "
    str_comando += "    AND tb_aux_ocorrencias_01.SubConta = tb_aux_ocorrencias_02.SubConta  "
    str_comando += "    AND tb_aux_ocorrencias_01.Situacao = tb_aux_ocorrencias_02.Situacao "
    str_comando += "WHERE "
    str_comando += "    tb_aux_ocorrencias_01.Data in " + str(tuple(dic_paginas[int_pagina]["Datas"]+[proporcao_aurea])) + " "
    str_comando += "    AND tb_aux_ocorrencias_01.Situacao = '" + dic_paginas[int_pagina]["Situacao"] + "' "
    str_comando += "GROUP BY "
    str_comando += "        tb_aux_ocorrencias_01.Data "
    str_comando += "        ,tb_aux_ocorrencias_01.SubConta "
    vet_saldos = executa_consulta(str_comando)

    # Converte saldos por dia/subconta em dicionário
    dic_saldos = {}
    for vet_saldo in vet_saldos:
        try:
            dic_saldos[vet_saldo[0]].append(vet_saldo[1:])
        except:
            dic_saldos[vet_saldo[0]] = []
            dic_saldos[vet_saldo[0]].append(vet_saldo[1:])

    str_texto_tela = ""
    int_cont = 0

    if len(dic_saldos.keys()) > 0:
        # Imprimir cabecalho das colunas
        str_texto_tela += "\n{}  {}  {}  {}  {}".format(formata_texto_posicoes("Seq", len(str(int_ocorrencias_por_pagina))+1, " ", "d")
                                                        ,formata_texto_posicoes("Data", 10, " ", "d")
                                                        ,formata_texto_posicoes("Sub-Conta", dic_larguras["SubConta"], " ", "d")
                                                        ,formata_texto_posicoes("O quê", dic_larguras["Oque"], " ", "d")
                                                        ,formata_texto_posicoes("Quanto", 10, " ", "a"))

    int_tracos = len(str(int_ocorrencias_por_pagina))+1 + 10 + dic_larguras["SubConta"] + dic_larguras["Oque"] + 10 + 8

    # flo_geral_acumulado = 0
    for str_data in dic_saldos.keys():
        str_texto_tela += "\n" + formata_texto_posicoes("-", int_tracos, "-", "d")

        for tup_subconta in dic_saldos[str_data]:
            str_subconta = tup_subconta[0]
            str_subconta_imprimir = formata_texto_posicoes(str_subconta, dic_larguras["SubConta"], " ", "d")
            str_saldo_subconta = tup_subconta[1]
            # flo_geral_acumulado += float(str_saldo_subconta)

            str_tracinhos = formata_texto_posicoes("-", len(str(int_ocorrencias_por_pagina))+1, "-", "d")
            str_saldo_subconta_constante = formata_texto_posicoes("Saldo subconta", dic_larguras["Oque"], " ", "d")

            # # Imprimir saldo da subconta
            # str_texto_tela += "\n{}  {}  {}  {}  {:10.2f}".format(str_tracinhos
            #                                                 ,str_data
            #                                                 ,str_subconta_imprimir
            #                                                 ,str_saldo_subconta_constante
            #                                                 ,float(str_saldo_subconta))

            # Imprime ocorrencias da subconta
            for tup_ocorrencia in dic_ocorrencias[str_data]:
                if tup_ocorrencia[0] == str_subconta:
                    str_o_que = formata_texto_posicoes(tup_ocorrencia[1], dic_larguras["Oque"], " ", "d")
                    str_valor = tup_ocorrencia[2]

                    int_cont += 1
                    str_cont = formata_texto_posicoes(str(int_cont), len(str(int_ocorrencias_por_pagina))+1, "0", "a")

                    str_texto_tela += "\n{}  {}  {}  {}  {:10.2f}".format(str_cont
                                                                    ,str_data
                                                                    ,str_subconta_imprimir
                                                                    ,str_o_que
                                                                    ,float(str_valor))

            # Define cor 'vermelha' para saldo de subconta negativo
            if float(str_saldo_subconta) < 0:
                str_na_cor = "\x1b[31m"
            else:
                str_na_cor = "\x1b[0m"

            # Imprimir saldo da subconta
            str_texto_tela += "\n{}  {}  {}  {}  {}{:10.2f}{}".format(str_tracinhos
                                                            ,str_data
                                                            ,str_subconta_imprimir
                                                            ,str_saldo_subconta_constante
                                                            ,str_na_cor
                                                            ,float(str_saldo_subconta)
                                                            ,"\x1b[0m"
                                                            )

            str_texto_tela += "\n"

        # # # Imprimir saldo geral acumulado
        # str_texto_tela += "\n{}  {:10.2f}".format(formata_texto_posicoes("Saldo Geral Acumulado", int_tracos - 12, " ", "d")
        #                                                 ,flo_geral_acumulado)

    return(str_texto_tela)


def string_data_em_iso8601(str_data):
    """Data uma string de data no formato DD/MM/AAAA, converte-a em TEXT como 
    ISO8601 string ('YYYY-MM-DD HH:MM:SS.SSS')
    """
    return(str_data[6:10] + "-" + str_data[3:5] + "-" + str_data[:2])


def abre_arquivo(str_arquivo):
    """Recebe o nome do arquivo, abre-o, e coloca em um vetor em que cada 
    posição é uma linha.
    
    Retorna no vetor e o último elemento tem um '\n' que depois precisa ser 
    tirado em cada processo específico.
    """

    str_arquivo = str(str_arquivo)
    vet_linhas = []

    try:
        with open(str_arquivo, 'r') as fil_arquivo:
            vet_linhas = fil_arquivo.readlines()
            fil_arquivo.close()

    except IOError:
        grava_log(("ERRO", "Problemas ao tentar ler o arquivo '" + str_arquivo + "'"))

    return vet_linhas


def grava_log(tup_log, bol_parar=False):
    """
    Recebe uma tupla com dois elementos, sendo o primeiro o tipo (info, ERRO, etc)
    """
    if tup_log[0] == "ERRO":
        str_na_cor = "\x1b[31m{}\x1b[0m".format(tup_log[0])
    elif tup_log[0] == "info":
        str_na_cor = "\x1b[32m{}\x1b[0m".format(tup_log[0])
    else:
        str_na_cor = tup_log[0]

    str_mensagem = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t" + str_na_cor + "\t" + tup_log[1] + "\n"
    print(str_mensagem)
    
    str_mensagem = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t" + tup_log[0] + "\t" + tup_log[1] + "\n"
    str_arquivo_log = "saidas/" + datetime.now().strftime("%Y%m%d") + "_processamento.log"

    if not bol_parar: #Se a chamada não foi feita por um erro de gravação de log
        try:
            with open(str_arquivo_log, 'a') as fLog:
                    fLog.write(str_mensagem)
                    fLog.close()
                    
                    if tup_log[0] == "ERRO":
                        sleep(2)
        except IOError:
            grava_log(("ERRO","AO GRAVAR Log {}".format(tup_log)), True)
            sleep(2)

    return


def importa_csv(str_nome_arquivo, str_tabela, vet_schema):
    """Acrescenta o conteudo de 'vet_arquivo' em uma estrutura de tabela definida:

    O leiaute do arquivo de entrada deve ser como segue:

    Data;Oque;Detalhe;SubConta;Valor;Situacao
    28/02/2020;Saldo Conta BRB;;BRB;1.385,99;Planejado
    28/02/2020;Saldo Conta Nubank;;Nubank;541,79;Planejado
    28/02/2020;Saldo Conta Santander;;Santander;308,41;REALIZADO
    """  
    
    global str_separador

    #Se a tabela ainda não existir vai ser criada
    cria_tabela(str_tabela, vet_schema)

    # TODO: Cria cópia de segurança dos dados carregados na base de ocorrências
    # TODO: Apaga registros correspondentes a cargas anteriores para a tabela

    vet_arquivo = abre_arquivo(str_nome_arquivo)

    for int_pos in range (1, len(vet_arquivo), 1):
        vet_campos = vet_arquivo[int_pos].split(str_separador)
        
        #Exclui o '\n' do ultimo campo
        vet_campos[-1] = vet_campos[-1].replace("\n","")

        # Quando se trata da tabela de ocorrencias, converte a data em TEXT 
        # como ISO8601 string ("YYYY-MM-DD HH:MM:SS.SSS") e substitui os 
        # pontos e vírgulas dos valores
        if str_tabela == "tb_ocorrencias":
            vet_campos[0] = string_data_em_iso8601(vet_campos[0])
            vet_campos[4] = vet_campos[4].replace(".","").replace(",",".")

        insere_registro_no_banco(str_tabela, vet_schema, vet_campos)


def cria_tabela(str_tabela, vet_campos, vet_tipos=[]):
    """Cria a tabela quando não existe
    """
    str_comando="CREATE TABLE IF NOT EXISTS " + str_tabela + " ("
    for int_cont in range(len(vet_campos)):
        str_comando += "\n    '"+vet_campos[int_cont] + "' "
        
        # Se os tipos dos campos forem passados por parâmetro, considera-os 
        # na criação da tabela, do contrário cria todos como tipo 'TEXT'
        if len(vet_tipos) > 0:
            str_comando += vet_tipos[int_cont]
        else:
            str_comando += "TEXT"

        if int_cont < len(vet_campos)-1:
            str_comando += ","

    str_comando += "\n)"

    str_mensagem_ok = "Tabela '{}' criada.".format(str_tabela)
    str_mensagem_erro = "Não foi possível criar a Tabela '{}'.".format(str_tabela)
    executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro)
    return


def insere_registro_no_banco(str_tabela, vet_campos, vet_valores):
    """Recebe o nome da tabela, um vetor com os nomes dos campos e outro com os valores
    e insere na base
    """
    
    #Elabora comando de insert
    str_comando="INSERT INTO " + str_tabela + " ("
    for int_cont in range(len(vet_campos)):
        str_comando+=vet_campos[int_cont]
        if int_cont < len(vet_campos)-1:
            str_comando += ","
    
    str_comando += ") VALUES ("

    for int_cont in range(len(vet_valores)):
        str_comando += "'"
        if type(vet_valores[int_cont]) == int:
            str_comando+=str(int(vet_valores[int_cont]))
        elif type(vet_valores[int_cont]) == float:
            str_comando+=str(vet_valores[int_cont])
            
        else:
            str_comando+=vet_valores[int_cont]
        str_comando+="'"
        if int_cont < len(vet_valores)-1:
            str_comando+=","

    str_comando += ")"
    print("str_comando: {}".format(str_comando))
    str_mensagem_ok = "Inserido registro na tabela '{}'.".format(str_tabela)
    str_mensagem_erro = "O registro nao foi inserido na tabela '{}'.".format(str_tabela)
    executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro)
    return

def executa_consulta(str_comando):
    """Recebe um comando SQL de consulta e o nome do banco, executa e retorna um vetor com os valores encontrados
    """  
    str_mensagem_ok = "Valores do select lidos para a memoria "
    str_mensagem_erro = "Nao foi possivel executar a consulta " + str_comando
    vet_registros = executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro)
    return(vet_registros)


def executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro):
    """Recebe um comando e o executa no banco de dados
    """
    global str_banco

    vet_registros=[]

    try:
        #Abre conexao com o banco
        conn = connect(str_banco)
        cursor = conn.cursor()
        
        #Executa o comando
        cursor.execute(str_comando)

        #Se eh uma consulta, atribui o resultado ao vetor
        if str_comando[:6] == "SELECT":
            vet_registros = cursor.fetchall()
            cursor.close()
        else:
            conn.commit()

        conn.close()

    except Error as error:
        grava_log(("ERRO", str_mensagem_erro + ": " + str(error)))
    finally:
        #Fecha a conexao com o banco independente de dar ou nao erro
        if (conn):
            conn.close()
    
    return(vet_registros)


def monta_tela(str_conteudo="", dic_opcoes={}, str_titulo="", int_pagina=0):
    """Monta a estrutura geral da 'janela' de interface

    - str_conteudo: preenchido com o que deve 'rechear' o 'miolo' da tela
    - dic_opcoes: as teclas aceitas na inteface (S)air, (V)oltar, etc
    - str_titulo: preenchido quando o título precisar ficar separado das opções
    """

    while True:
        system("clear") or None
        print(str_titulo, end="")
        print(str_conteudo)
        str_escolha = input("\nDigite a opção (que está entre parêntesis): ").upper()

        if not str_escolha in dic_opcoes.keys() :
            #A opção digitada não consta do rol de opções da tela em questão
            print("\nA opção digitada '{}' não está prevista!".format(str_escolha))
            sleep(2)
        
        #Invoca cada uma das opções previstas
        else:
            # Paginação para menos
            if dic_opcoes[str_escolha] == "extrato_menos_1":
                int_pagina -= 1
                dic_opcoes[str_escolha] = "extrato"

            # Paginação para mais
            if dic_opcoes[str_escolha] == "extrato_mais_1":
                int_pagina += 1
                dic_opcoes[str_escolha] = "extrato"

            # Todas as opções válidas
            if dic_opcoes[str_escolha] == "sair":
                print("\nObrigado por usar o aplicativo! Até logo!")
                sleep(2)
                exit()

            elif dic_opcoes[str_escolha] == "voltar_extrato":
                menu_iniciar()

            elif dic_opcoes[str_escolha] == "menu_iniciar_configuracoes":
                str_configuracoes  = "Configurações:\n\n"
                str_configuracoes += "(I)mportar .csv\n"
                str_configuracoes += "(E)xportar .csv\n"
                str_configuracoes += "E(x)cluir backups\n"
                str_configuracoes += "(C)ontas e sub-contas\n"
                str_configuracoes += "(V)oltar\n"

                monta_tela(str_configuracoes, {   "I": "configuracoes_importar"
                                                , "E": "configuracoes_exportar"
                                                , "X": "configuracoes_excluir_backups"
                                                , "C": "configuracoes_contas_e_subcontas"
                                                , "V": "voltar"})

            elif dic_opcoes[str_escolha] == "configuracoes_importar":
                # TODO: Alterar para relacionar os arquivos disponíveis e 
                # permitir que o usuário escolha

                importa_csv("ocorrencias.csv", "tb_ocorrencias", [  "Data", 
                                                                    "Oque", 
                                                                    "Detalhe", 
                                                                    "SubConta", 
                                                                    "Valor", 
                                                                    "Situacao"])

            elif dic_opcoes[str_escolha] == "voltar":
                break

            elif dic_opcoes[str_escolha] == "extrato":
                # Só monta as páginas na primeira vez que entra em extrato
                if int_pagina == 0:
                    monta_paginas_extrato()
                    int_pagina += 1

                dic_opcoes_proximo = {"A": "extrato_menos_1"
                                    , "P": "extrato_mais_1"
                                    , "E": "extrato_editar_ocorrencia"
                                    , "I": "inserir_ocorrencia"
                                    , "V": "voltar_extrato"}

                if int_pagina > 0:
                    str_extrato = carrega_extrato(int_pagina)

                str_extrato += "\n\n"

                # Só exibe a opção se tiver páginas antes
                if int_pagina > 1:
                    str_extrato += "Página (A)nterior\n"

                else:
                    dic_opcoes_proximo.pop("A")

                # Só exibe a opção se tiver páginas depois
                if int_pagina < len(dic_paginas.keys()):
                    str_extrato += "(P)róxima Página\n"

                else:
                    dic_opcoes_proximo.pop("P")

                str_extrato += "(E)ditar ocorrência\n"  #TODO: Só quando tiverem ocorrências sendo exibidas
                str_extrato += "(I)nserir\n"
                str_extrato += "(V)oltar\n"

                monta_tela(str_extrato, dic_opcoes_proximo, "Extrato: {}\n".format(dic_paginas[int_pagina]["Situacao"]), int_pagina)

            elif dic_opcoes[str_escolha] == "configuracoes_contas_e_subcontas":
                #TODO: montar relação de contas e sub-contas

                str_contas_e_subcontas  = "(E)ditar sub-conta\n"    #TODO: Só quando tiverem contas/sub-contas
                str_contas_e_subcontas += "(A)crescentar sub-conta\n"
                str_contas_e_subcontas += "(V)oltar\n"

                monta_tela(str_contas_e_subcontas, {  "E": "contas_e_subcontas_editar"
                                                    , "A": "contas_e_subcontas_acrescentar"
                                                    , "V": "voltar"}, "Contas e sub-contas:\n\n")

            else:
                #TODO: Avaliar se depois de todas as opções implementadas,  é meso necessário manter este else
                print("\nFuncionalidade '{} - {}' ainda não implementada".format(str_escolha, dic_opcoes[str_escolha]))
                sleep(2)


def menu_iniciar():
    str_menu_inicial  = "Menu Inicial:\n\n"
    str_menu_inicial += "(C)onfigurações\n"
    str_menu_inicial += "(E)xtrato\n"
    str_menu_inicial += "(I)nserir\n"
    str_menu_inicial += "(S)air\n"
    monta_tela(str_menu_inicial, {    "C": "menu_iniciar_configuracoes"
                                    , "E": "extrato"
                                    , "I": "inserir_ocorrencia"
                                    , "S": "sair"})

if __name__ == "__main__":
    menu_iniciar()