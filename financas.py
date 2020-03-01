#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""O script mantém um fluxo de caixa de finanças pessoais, bem como as funções
de interação com ele, como algumas das funcionalidades abaixo relacionadas:

- Inserir novas ocorrências
- Alterar ocorrências
- Visualizar extrato
- Definir saldo de contas
"""

from os import system
from time import sleep
from datetime import datetime
from sqlite3 import connect, Error
# from io import open
# from json import load

str_banco = "financas.db"
str_separador = ";"

def carrega_extrato():
    """
    TODO: Escrever arrazoado sobre o método
    TODO: Ajustar para apresentar primeiro o que é planejado e só depois o que é realizado
    TODO: Bolar paginação
    """
    # Consulta os saldos finais das subcontas por dia
    str_comando  = "SELECT "
    str_comando += "        tb_aux_ocorrencias_01.Data "
    str_comando += "        ,tb_aux_ocorrencias_01.SubConta "
    str_comando += "        ,SUM(tb_aux_ocorrencias_02.Valor) AS 'Valor' "
    str_comando += "        ,tb_aux_ocorrencias_01.Situacao "
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
    # TODO: A cláusua abaixo precisa ser repensada para ter condições de 
    # mostrar todos os lançamentos
    str_comando += "        tb_aux_ocorrencias_01.Situacao = 'Planejado' " 
    str_comando += "GROUP BY "
    str_comando += "        tb_aux_ocorrencias_01.Data "
    str_comando += "        ,tb_aux_ocorrencias_01.SubConta "
    str_comando += "        ,tb_aux_ocorrencias_01.Situacao "
    vet_saldos = executa_consulta(str_comando)

    # Identifica as datas para as quais tem ocorrências
    vet_datas = []
    for vet_saldo in vet_saldos:
        vet_datas.append(vet_saldo[0])
    
    vet_datas = list(set(vet_datas))
    vet_datas.sort()

    str_texto_tela = ""

    # Para cada com ocorrências, imprime
    for str_data in vet_datas:
        # Consulta todos os registros de ocorrênicas para a data.
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
        str_comando += "    Data = " + "'" + str_data + "'"
        str_comando += "ORDER BY "
        str_comando += "    Situacao ASC "
        str_comando += "    ,SubConta "
        # str_comando += "    ,Data ASC "
        str_comando += "    ,Valor DESC "
        vet_registros = executa_consulta(str_comando)

        int_cont = 0
        str_subconta = "xxx"
        str_texto_tela += "\n" + "-"*50
        for vet_registro in vet_registros:
            if str_subconta != vet_registro[1]:
                str_subconta = vet_registro[1]
                str_texto_tela += "\n{}\t{}\t{}\t{}\t{}".format("--", 
                                                                vet_registro[0], 
                                                                vet_registro[1], 
                                                                "Saldo subconta", 
                                                                "vet_saldos[???]") # TODO: Ajustar para apresentar o saldo da conta


            int_cont += 1
            str_texto_tela += "\n{}\t{}\t{}\t{}\t{}".format(int_cont, 
                                                vet_registro[0], 
                                                vet_registro[1], 
                                                vet_registro[2], 
                                                vet_registro[3])
            
        
        # TODO: Inserir também o saldo da conta

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
    from time import sleep

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
    """Acrescenta o conteudo de 'vet_arquivo' em uma estrutura de tabela definida
    """  
    
    global str_separador

    #Se a tabela ainda não existir vai ser criada
    cria_tabela(str_tabela, vet_schema)

    #Cria cópia de segurança dos dados carregados na base de ocorrências
    # TODO

    # #Apaga registros correspondentes a cargas anteriores para a tabela
    # exclui_registros_anteriores(str_tabela)

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


def exclui_registros_anteriores(str_tabela, sOutrasClausulas=""):
    """Recebe o nome da tabela e exclui todos os seus registros.
    """
    str_comando="DELETE FROM " + str_tabela + " WHERE AnoMes = '" + sAnoMes + "' " + sOutrasClausulas + " "
    str_mensagem_ok = "Apagados registros anteriores da tabela '" + str_tabela + "' onde AnoMes = '" + sAnoMes + "' "
    str_mensagem_erro = "Nao foram excluidos os registros anteriores da tabela '" + str_tabela + "' onde AnoMes = '" + sAnoMes + "' "
    executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro)
    return


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
    """
    Recebe um comando SQL de consulta e o nome do banco, executa e retorna um vetor com os valores encontrados
    """  
    str_mensagem_ok = "Valores do select lidos para a memoria "
    str_mensagem_erro = "Nao foi possivel executar a consulta " + str_comando[:80] + "..."  
    vet_registros=executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro)
    return(vet_registros)


def executa_comando_banco(str_comando, str_mensagem_ok, str_mensagem_erro):
    """
    Recebe um comando e o executa no banco de dados
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
        # grava_log(("info", str_mensagem_ok))
    except Error as error:
        grava_log(("ERRO", str_mensagem_erro + ": " + str(error)))
    finally:
        #Fecha a conexao com o banco independente de dar ou nao erro
        if (conn):
            conn.close()
    
    return(vet_registros)


# def exporta_tabela_para_csv(vetTabela, vet_campos, str_arquivoSaida):
#     """
#     Recebe um vetor de dados, outro dos titulos dos campos e o nome do arquivo de saida
#     e gera um arquivo de saida, separando os campos por pipe
#     """
#     sLinhas = u""
#     for int_cont in range(len(vet_campos)):
#         sLinhas+=vet_campos[int_cont]
#         if int_cont < len(vet_campos)-1:
#             sLinhas+="|"

#     sLinhas+="\n"

#     for vetLinha in vetTabela:
#         for int_cont in range (len(vetLinha)):
#             if type(vetLinha[int_cont]) == float:
#                 sLinhas += str(vetLinha[int_cont]).replace(".", ",")
#             else:
#                 sLinhas += str(vetLinha[int_cont])
#             if int_cont < len(vet_campos)-1:
#                 sLinhas+="|"
#             else:
#                 sLinhas+="\n"

#     escreveArquivo(str_arquivoSaida, sLinhas)


# def escreveArquivo(sNome, sConteudo, bSobrescreve=True):
#     """
#     Recebe um nome de arquivo e o conteudo a ser escrito e escreve no arquivo
#     Observacao: O default eh sobrescrever o arquivo, se quiser add, tem que passar o parametro bSobrescreve=False
#     """
#     sArquvo = "saidas/"+sNome
#     bArquivoExiste = False
#     if bSobrescreve:
#         sModo = "w"
#     else:
#         sModo = "a"

#     try:
#         with open("saidas/"+sNome, sModo) as fil_arquivo:     #Aberto com with, nao precisa do close
#             fil_arquivo.write(sConteudo)
#             fil_arquivo.close()
#             grava_log(("info", "Arquivo '" + "saidas/" + sNome + "' gravado com sucesso "))

#     except IOError:
#         grava_log(("ERRO", "Nao foi possivel gravar no arquivo '" + "saidas/" + sNome + "'"))


def monta_tela(str_conteudo="", dic_opcoes={}, str_titulo=""):
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
            if dic_opcoes[str_escolha] == "menu_iniciar_sair":
                print("\nObrigado por usar o aplicativo! Até logo!")
                sleep(2)
                break

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

            elif dic_opcoes[str_escolha] == "menu_iniciar_extrato":
                str_extrato = carrega_extrato()         #TODO: montar extrato/paginação

                str_extrato += "Página (A)nterior\n"    #TODO: Só quando tiverem datas/valores anteriores
                str_extrato += "(P)róxima Página\n"     #TODO: Só quando tiverem datas/valores posteriores
                str_extrato += "(E)ditar ocorrência\n"  #TODO: Só quando tiverem ocorrências sendo exibidas
                str_extrato += "(I)nserir\n"
                str_extrato += "(V)oltar\n"

                monta_tela(str_extrato, { "A": "extrato_pagina_anterior"
                                        , "P": "extrato_proxima_pagina"
                                        , "E": "extrato_editar_ocorrencia"
                                        , "I": "inserir_ocorrencia"
                                        , "V": "voltar"}, "Extrato:\n\n")

            elif dic_opcoes[str_escolha] == "configuracoes_contas_e_subcontas":
                print("")                                           #TODO: montar relação de contas e sub-contas

                str_contas_e_subcontas  = "(E)ditar sub-conta\n"    #TODO: Só quando tiverem contas/sub-contas
                str_contas_e_subcontas += "(A)crescentar sub-conta\n"
                str_contas_e_subcontas += "(V)oltar\n"

                monta_tela(str_contas_e_subcontas, {  "E": "contas_e_subcontas_editar"
                                                    , "A": "contas_e_subcontas_acrescentar"
                                                    , "V": "voltar"}, "Contas e sub-contas:\n\n")

            else:
                print("\nFuncionalidade '{} - {}' ainda não implementada".format(str_escolha, dic_opcoes[str_escolha]))
                sleep(2)
                pass                                    #TODO: Avaliar se depois de todas as opções implementadas,  é meso necessário manter este else


if __name__ == "__main__":
    str_menu_inicial  = "Menu Inicial:\n\n"
    str_menu_inicial += "(C)onfigurações\n"
    str_menu_inicial += "(E)xtrato\n"
    str_menu_inicial += "(I)nserir\n"
    str_menu_inicial += "(S)air\n"
    monta_tela(str_menu_inicial, {    "C": "menu_iniciar_configuracoes"
                                    , "E": "menu_iniciar_extrato"
                                    , "I": "inserir_ocorrencia"
                                    , "S": "menu_iniciar_sair"})