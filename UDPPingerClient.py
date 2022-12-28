import socket
from time import *
import statistics as stat

#Variaveis Auxiliares
serverName = '127.0.0.1'
serverPort = 30000
numPacotes = 10
tempoEspera = 1
perdaPacote = 0
contador = 0
startingTime = time()
mensagemOriginal = 'RicardoMagal'

#Listas (Para RTT e para pacotes recebidos)
RTTList = []
recebidosList = []


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Tolerancia de espera por pacotes de 1 segundo
clientSocket.settimeout(tempoEspera)
while True:
    contador += 1
    #Condicao de parada do loop. No caso, o cliente espera ate enviar e tentar receber o ultimo pacote para desistir dos perdidos
    if (contador > numPacotes):
        perdaPacote = numPacotes - len(recebidosList)
        break
    ################## Construcao do pacote ##################
    sequencia = str(contador).zfill(5)
    tempoEnviado = str(int((time() - startingTime)*1000)).zfill(4) #Comeca a contar o RTT (Escolhi um tempo arbitrario para subtrair, limitando o tamanho do int)
    mensagem = mensagemOriginal
    ping = '0'
    pacote = sequencia + ping + tempoEnviado + mensagem
    pacote = str.encode(pacote)
    ###########################################################
    clientSocket.sendto(pacote, (serverName, serverPort))
    print('ENVIADO  | Sequencia:', sequencia, '| 0 |', tempoEnviado, 'ms | Mensagem:', mensagem)
    #Tenta receber uma mensagem do servidor, mas levanta uma excecao caso o tempo de espera exceda o colocado.
    try:
        pacote, serverAddress = clientSocket.recvfrom(40) #Pacote fixado para 40 bytes
    except socket.timeout:
        print("Pacote atrasado!")
        continue
    except Exception as e:
        print(e)
        continue
    #Imprime uma requisicao Pong, coloca o RTT do pacote na lista e atualiza lista de pacotes recebidos
    tempoRecebido = int((time()-startingTime)*1000)
    try:
        sequencia, pong, timestamp, mensagem = pacote[:5].decode('utf-8'), chr(pacote[5]), pacote[6:10].decode('utf-8'), pacote[10:].decode('utf-8')
    except Exception:
        print("Formatacao errada!")
        continue
    if(pong!='1' or mensagem!=mensagemOriginal):
        print("Pacote Invalido!")
        continue
    recebidosList.append(sequencia)
    print('RECEBIDO | Sequencia:', sequencia, '|', pong, '|', str(tempoRecebido).zfill(4) , 'ms | Mensagem:', mensagem)
    RTTList.append(int(tempoRecebido) - int(timestamp))

#Print final
if len(recebidosList) >0:
    print(numPacotes, 'packets transmitted,', numPacotes - perdaPacote, 'received,', (perdaPacote/numPacotes)*100,'% packet loss, time,', round(sum(RTTList),3),'ms rtt min/avg/max/mdev =', round(min(RTTList),3), '/',round(sum(RTTList)/len(RTTList),3), '/',round(max(RTTList),3), '/', round(stat.stdev(RTTList),3))
else:
    print(numPacotes, 'packets transmitted,', numPacotes - perdaPacote, 'received')
clientSocket.close()