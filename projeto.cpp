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
///
/// Esta classe encapsula a leitura de um canal ADC do Linux IIO (Industrial I/O)
/// e fornece uma função para obter o valor lido.
class LerADC {
    std::string caminho; ///< Caminho completo para o arquivo do canal ADC.

public:
    /// @brief Construtor da classe LerADC.
    /// @param canal_adc Número do canal ADC (ex.: 13 para in_voltage13_raw).
    explicit LerADC(int canal_adc) {
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

/// @brief Função principal.
///
/// Cria um leitor de ADC, lê valores periodicamente e envia via UDP
/// para um PC remoto. No terminal, exibe o valor lido e indica presença
/// quando o valor está acima do limiar.
///
/// @return 0 em caso de sucesso, 1 em caso de erro na criação do socket.
int main() {
    int canal_adc = 13;
    LerADC sensor(canal_adc);

    // Criação do socket UDP
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    // Configuração do endereço do PC destino
    sockaddr_in servidorPC{};
    servidorPC.sin_family = AF_INET;
    servidorPC.sin_port = htons(5000);              ///< Porta destino
    servidorPC.sin_addr.s_addr = inet_addr("192.168.42.10"); ///< IP do PC

    const int limiar_presenca = 60000; ///< Valor acima do qual há presença

    while (true) {
        int valor = sensor.ler();

        if (valor >= 0) {
            // Monta mensagem CSV: "adc,<valor>"
            std::string msg = "adc," + std::to_string(valor) + "\n";

            // Envia CSV via UDP
            sendto(sock, msg.c_str(), msg.size(), 0, (sockaddr*)&servidorPC, sizeof(servidorPC));

            // Exibe no terminal
            std::cout << "Valor ADC: " << valor << " (enviado: " << msg << ")" << std::endl;

            // Detecta presença
            if (valor > limiar_presenca) {
                std::cout << ">>> Presenca detectada!\n";
            } else {
                std::cout << "Sem presenca.\n";
            }
        }

        // Espera 2 segundos entre leituras
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    return 0;
}
