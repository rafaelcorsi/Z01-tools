# -*- coding: utf-8 -*-
# Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
#
# script para gerar hack a partir de nasm
# suporta como entrada um único arquivo
# ou um diretório
# Possibilita também a geração do .mif

import os,sys
import argparse
from termcolor import colored
import time

from config import *
from util import *
from simulateCPU import simulateCPU
from log import logError, logTest, logSim

def clearTestDir(testDir):
    configFile = testDir+CONFIG_FILE
    pwd = os.path.dirname(configFile)+"/"
    f = openConfigFile(testDir)

    if f is not False:
            for l in f:
                if len(l.strip()):
                    if l.strip()[0]!='#':
                        if (l.strip().find('.nasm') > 0):
                            par   = l.rstrip().split();
                            name  = par[0][:-5]
                            nTest = int(par[1])
                            for i in range (0, nTest):
                                nameTest   = name + str(i)
                                ramEndSimu = pwd + "tst/" + name + "/" + nameTest + RAM_END_SIMU_FILE
                                try:
                                    os.remove(ramEndSimu)
                                except:
                                    pass
    else:
        return(-1)

# Compara dois arquivos RAM em busca
# de diferencas. Só verifica os endereços
# especificados em ramEnd
def compareRam(name, ramEnd, ramEndSimulation):
    # file
    fS = ""
    fE = ""

    # list
    ram = {}
    validacao = {}

    try:
        fS = open(ramEndSimulation, 'r')
    except:
        logError("Arquivo {} não encontrado".format(ramEndSimulation))
        return(False)

    # verifica se existe arquivos
    try:
        fE = open(ramEnd, 'r')
    except:
        logError("Arquivo {} não encontrado".format(ramEnd))
        return(False)

    # cria um vetor a partir do esperado da memória (.mif)
    for linha in fE:
        if linha.find(":") > 0:
                alocacao = linha.split(":")
                ram[int(alocacao[0].strip())] = alocacao[1].strip().replace(';','')

    # cria um vetor a partir do resultado da simulação
    for l in fS:
        if l.find(":") > 0:
                alocacao = l.split(":")
                validacao[int(alocacao[0].strip())] = alocacao[1].strip()

    # compara as memórias criadas buscando por diferencas
    for e, v in ram.items():
            if(ram[e] != validacao[e]):
                    print(colored(" FALHOU: {}".format(name) , 'red'))
                    print(" RAM     : {}".format(e))
                    print(" esperado: " + ram[e])
                    print(" obtido  : " + validacao[e])
                    print(colored(" ---------------------", 'red'))
                    return(False)
    return(True)


# Recebe como parametro um diretorio do tipo teste
# e faz a comparação de todos os testes especificados
# no arquivo de configuração
def compareFromTestDir(testDir, nasmFile=None):

    # caminho do arquivo de configuracao
    configFile = testDir+CONFIG_FILE
    pwd = os.path.dirname(configFile)+"/"
    log = []
    error = 0

    f = openConfigFile(testDir)

    if f is not False:
        for l in f:
            if len(l.strip()):
                if l.strip()[0]!='#':
                    if (l.strip().find('.nasm') > 0) or (l.strip().find('.vm') > 0):
                        par   = l.rstrip().split()
                        if(l.strip().find('.vm') > 0 ):
                            name = par[0][:-3]
                        else:
                            name = par[0][:-5]
                        nTest = int(par[1])

                        # verifica se é para executar compilar
                        # apenas um arquivo da lista
                        if nasmFile is not None:
                            if name != nasmFile:
                                continue
                           
                        for i in range (0, nTest):
                            nameTest   = name + str(i)
                            ramEnd     = pwd + "/tst/" + name + "/" + name + "{}".format(i) + RAM_END_FILE
                            ramEndSimu = pwd + "/tst/" + name + "/" + nameTest + RAM_END_SIMU_FILE
                            if(os.path.isfile(ramEnd) and os.path.isfile(ramEndSimu)):
                                print(' - Testando {}'.format(name))
                                rtn = compareRam(nameTest, ramEnd, ramEndSimu)
                                r = "Teste Ok" if rtn else "Teste Falha"
                                result = {'name':name, 'status':rtn, 'teste':i}
                                log.append(result)
                                if not rtn:
                                    error = error + 1
    else:
        return -1, result

    print("\n=-=- Summary =-=-=")
    for result in log:
        if result['status']:
            print(colored("pass",'green') + "    {} teste: {}".format(result['name'], result['teste']))
        else:
            print(colored("fail",'red') + "    {} teste {}".format(result['name'], result['teste']))
    return error, log
