## @file servidor_udp.py
#  @brief Servidor UDP para recepção de pacotes enviados por dispositivo remoto.
#
#  Este script recebe mensagens UDP enviadas por outro programa (por exemplo, um
#  dispositivo que transmite dados de leitura de sensores) e exibe o conteúdo no
#  terminal. As mensagens são recebidas no formato CSV, como "adc,valor,estado".
#
#  O servidor pode ser executado em qualquer computador conectado à mesma rede
#  do transmissor. Ele escuta continuamente em uma porta UDP definida e mostra
#  o IP de origem e a mensagem recebida.
#
#  @author Eduardo
#  @date 2025
#  @version 1.0

import socket

## @brief Função principal do servidor UDP.
#
#  Cria um socket UDP, associa-o a uma porta e aguarda pacotes de dados.
#  A cada pacote recebido, imprime no terminal o IP de origem, a porta e
#  a mensagem recebida (decodificada como texto).
#
#  O servidor pode ser interrompido com Ctrl+C.
#
#  @return Nenhum valor é retornado. O programa roda indefinidamente até ser interrompido.
def main():
    ## @var IP_LOCAL
    #  Endereço IP onde o servidor escuta (0.0.0.0 = todas as interfaces).
    IP_LOCAL = "0.0.0.0"

    ## @var PORTA
    #  Porta UDP na qual o servidor recebe as mensagens.
    PORTA = 5000

    ## @brief Criação e configuração do socket UDP.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_LOCAL, PORTA))

    print(f"Servidor UDP aguardando dados em {IP_LOCAL}:{PORTA} ...\n")

    try:
        ## @brief Loop principal de recepção de pacotes UDP.
        #
        #  O servidor fica bloqueado em `recvfrom()` até a chegada de um pacote.
        #  Quando um pacote é recebido, ele é decodificado e exibido no terminal.
        while True:
            ## @var data
            #  Dados recebidos em bytes.
            ## @var endereco
            #  Tupla (ip, porta) do remetente.
            data, endereco = sock.recvfrom(1024)
            mensagem = data.decode(errors="ignore").strip()

            print(f"📩 Pacote recebido de {endereco[0]}:{endereco[1]}")
            print(f"   Mensagem: {mensagem}\n")

    except KeyboardInterrupt:
        ## @brief Tratamento de interrupção manual (Ctrl+C).
        print("\nEncerrando servidor UDP...")

    finally:
        ## @brief Fecha o socket antes de encerrar o programa.
        sock.close()


## @brief Ponto de entrada do programa.
#
#  Garante que a função principal só seja executada quando o script for
#  executado diretamente (e não importado como módulo).
if __name__ == "__main__":
    main()
