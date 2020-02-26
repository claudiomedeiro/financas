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

def monta_tela(str_conteudo="", dic_opcoes={}, str_titulo=""):
    """Monta a estrutura geral da 'janela' de interface

    - str_conteudo: preenchido com o que deve 'rechear' o 'miolo' da tela
    - dic_opcoes: as teclas aceitas na inteface (S)air, (V)oltar, etc
    - str_titulo: preenchido quando o título precisar ficar separado das opções
    """

    while True:
        system('clear') or None
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
                                                , "V": "configuracoes_voltar"})

            elif dic_opcoes[str_escolha] == "configuracoes_voltar":
                break

            elif dic_opcoes[str_escolha] == "menu_iniciar_extrato":
                print("")                               #TODO: montar extrato/paginação

                str_extrato  = "Página (A)nterior\n"    #TODO: Só quando tiverem datas/valores anteriores
                str_extrato += "(P)róxima Página\n"     #TODO: Só quando tiverem datas/valores posteriores
                str_extrato += "(E)ditar ocorrência\n"  #TODO: Só quando tiverem ocorrências sendo exibidas
                str_extrato += "(V)oltar\n"

                monta_tela(str_extrato, { "A": "extrato_pagina_anterior"
                                        , "P": "extrato_proxima_pagina"
                                        , "E": "extrato_editar_ocorrencia"
                                        , "V": "extrato_voltar"}, "Extrato:\n\n")

            elif dic_opcoes[str_escolha] == "extrato_voltar":
                break

            elif dic_opcoes[str_escolha] == "configuracoes_contas_e_subcontas":
                print("")                                           #TODO: montar relação de contas e sub-contas

                str_contas_e_subcontas  = "(E)ditar sub-conta\n"    #TODO: Só quando tiverem contas/sub-contas
                str_contas_e_subcontas += "(A)crescentar sub-conta\n"
                str_contas_e_subcontas += "(V)oltar\n"

                monta_tela(str_contas_e_subcontas, {  "E": "contas_e_subcontas_editar"
                                                    , "A": "contas_e_subcontas_acrescentar"
                                                    , "V": "contas_e_subcontas_voltar"}, "Contas e sub-contas:\n\n")

            elif dic_opcoes[str_escolha] == "contas_e_subcontas_voltar":
                break

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
                                    , "I": "menu_iniciar_inserir"
                                    , "S": "menu_iniciar_sair"})