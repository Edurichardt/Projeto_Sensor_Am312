#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>


/// @class LerADC
/// @brief Classe responsável por ler valores analógicos do ADC.
class LerADC {
    /// Caminho completo para o arquivo do canal ADC.
    std::string caminho;

public:
    /// @brief Construtor da classe LerADC.
    /// @param canal_adc Número do canal ADC (in_voltage13_raw).
    LerADC(int canal_adc) {
        caminho = "/sys/bus/iio/devices/iio:device0/in_voltage" 
                  + std::to_string(canal_adc) + "_raw";
    }

    /// @brief Lê o valor atual do ADC.
    /// @return Valor inteiro lido do ADC. Retorna -1 em caso de erro.
    int ler() {
        std::ifstream file(caminho);
        if (!file.is_open()) {
            std::cerr << "Erro ao abrir " << caminho << std::endl;
            return -1;
        }
        int valor;
        file >> valor;
        return valor;
    }
};

/// @brief Função principal. Cria um leitor de ADC de uma STM32 com um sensor Am312 conectado
/// lê seu valor periodicamente e envia via UDP para um PC remoto em formato CSV.
/// @return 0 em caso de sucesso, 1 em caso de erro.
int main() {
    int canal_adc = 13;  ///< Canal ADC
    LerADC sensor(canal_adc);

    // Inicialização do socket

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    // Configura endereço do PC destino, para quando eu for enviar 
    sockaddr_in servidorPC{};
    servidorPC.sin_family = AF_INET;
    servidorPC.sin_port = htons(5000);              ///< Porta destino (5000).
    servidorPC.sin_addr.s_addr = inet_addr("192.168.42.10"); ///< IP do PC destino.

    while (true) {
        // Lê valor do ADC
        int valor = sensor.ler();

        if (valor >= 0) {
            /// Monta linha CSV: "adc,<valor>"
            std::string msg = "adc," + std::to_string(valor) + "\n";

            // Envia CSV via UDP, posteriormente vai para a interface em python, que ainda não está pronta
            sendto(sock, msg.c_str(), msg.size(), 0, (sockaddr*)&servidorPC, sizeof(servidorPC));

            // No terminal da placa, vai printar o nível adc e, em caso de saída alta (máxima tensão), indica que há presença
            std::cout << "Valor ADC: " << valor << " (enviado: " << msg << ")" << std::endl;
            if (nivel_adc > 60000) {  
            printf(">>> Presenca detectada!\n");
            } else {
            printf("Sem presenca.\n");

        }

        std::this_thread::sleep_for(std::chrono::seconds(2)); // leitura a cada 2s (timer)
    }


    return 0;
}
