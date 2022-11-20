import socket
import sys
from time import *
import statistics as stat

#Variaveis Auxiliares
serverName = '127.0.0.1'
serverPort = 30000
numPacotes = 10
tempoEspera = 1
perdaPacote = 0
contador = 0

#Listas (Para RTT e para pacotes recebidos)
RTTList = []
recebidosList = []


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Tolerancia de espera por pacotes de 1 segundo
clientSocket.settimeout(tempoEspera)
while True:
    contador += 1
    ################## Construcao do pacote ##################
    sequencia = contador.to_bytes(5, 'big')
    tempoEnviado = int((time() - 1668971305)*1000).to_bytes(4,'big')  #Comeca a contar o RTT (Escolhi um tempo arbitrario para subtrair, limitando o tamanho do int)
    mensagem = bytes('Ping', 'ascii')
    ping = bytes('0', 'ascii')
    pacote = sequencia + ping + tempoEnviado + mensagem
    ###########################################################
    clientSocket.sendto(pacote, (serverName, serverPort))
    print('ENVIADO  | Sequencia:', "%2d" % (int.from_bytes(sequencia,'big'),), '| 0 |', int.from_bytes(tempoEnviado, 'big'), 'ms | Mensagem:', mensagem.decode('ascii'))
    #Tenta receber uma mensagem do servidor, mas levanta uma excecao caso o tempo de espera exceda o colocado.
    try:
        pacote, serverAddress = clientSocket.recvfrom(40) #Pacote fixado para 40 bytes
        if(sys.getsizeof(pacote)!=40):
            print("Pacote inconsistente!")
            continue
    except socket.timeout:
        print("Pacote atrasado!")
        continue
    #Imprime uma requisicao Pong, coloca o RTT do pacote na lista e atualiza lista de pacotes recebidos
    tempoRecebido = (time()-1668971305)*1000
    sequencia, pong, timestamp, mensagem = int.from_bytes(pacote[:5],'big'), chr(pacote[5]), int.from_bytes(pacote[6:10], 'big'), pacote[10:]
    recebidosList.append(sequencia)
    print('RECEBIDO | Sequencia:', "%2d" % (sequencia,), '|', pong, '|', int(tempoRecebido), 'ms | Mensagem:', mensagem.decode('ascii'))
    RTTList.append(tempoRecebido - timestamp)
    #Condicao de parada do loop. No caso, o cliente espera ate enviar o ultimo pacote para desistir dos perdidos
    if(contador>=numPacotes):
        perdaPacote = numPacotes - len(recebidosList)
        break

#Print final
print(numPacotes, 'packets transmitted,', numPacotes - perdaPacote, 'received,', (perdaPacote/numPacotes)*100,'% packet loss, time,', round(sum(RTTList),3),'ms rtt min/avg/max/mdev =', round(min(RTTList),3), '/',round(sum(RTTList)/len(RTTList),3), '/',round(max(RTTList),3), '/', round(stat.stdev(RTTList),3))
clientSocket.close()