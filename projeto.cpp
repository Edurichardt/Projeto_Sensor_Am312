/**
 * @file main.cpp
 * @brief Leitor de ADC e envio periódico via UDP.
 *
 * Este programa lê valores de um canal ADC do sistema Linux (IIO) e envia
 * periodicamente as leituras via UDP para um computador remoto. O valor
 * é comparado com um limiar para indicar presença.
 *
 * @author Eduardo
 * @date 2025
 */

#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

/**
 * @class LerADC
 * @brief Classe responsável por ler valores analógicos do ADC.
 *
 * Esta classe encapsula a leitura de um canal ADC do subsistema IIO
 * (Industrial I/O) do Linux. O valor é lido diretamente de um arquivo
 * de dispositivo localizado em `/sys/bus/iio/devices/`.
 */
class LerADC {
    std::string caminho; ///< Caminho completo para o arquivo do canal ADC.

public:
    /**
     * @brief Construtor da classe LerADC.
     * @param canal_adc Número do canal ADC (ex.: 13 para `in_voltage13_raw`).
     *
     * Inicializa o caminho do arquivo correspondente ao canal ADC informado.
     */
    explicit LerADC(int canal_adc) {
        caminho = "/sys/bus/iio/devices/iio:device0/in_voltage"
                 + std::to_string(canal_adc) + "_raw";
    }

    /**
     * @brief Lê o valor atual do ADC.
     * @return Valor inteiro lido do ADC. Retorna -1 em caso de erro.
     *
     * Abre o arquivo correspondente ao canal e lê o valor numérico.
     */
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

/**
 * @brief Função principal.
 *
 * Cria um leitor de ADC, lê valores periodicamente e envia via UDP
 * para um PC remoto. Também exibe no terminal local o valor lido e
 * indica quando há presença detectada.
 *
 * @return 0 em caso de sucesso, 1 em caso de erro na criação do socket.
 */
int main() {
    const int canal_adc = 13;                ///< Canal ADC a ser lido.
    const int limiar_presenca = 60000;       ///< Valor acima do qual há presença.
    const int porta_destino = 5000;          ///< Porta UDP do servidor destino.
    const std::string ip_destino = "192.168.42.10"; ///< IP do servidor destino.

    LerADC sensor(canal_adc);

    // === Criação do socket UDP ===
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    // === Configuração do endereço do servidor destino ===
    sockaddr_in servidorPC{};
    servidorPC.sin_family = AF_INET;
    servidorPC.sin_port = htons(porta_destino);
    servidorPC.sin_addr.s_addr = inet_addr(ip_destino.c_str());

    std::cout << "Iniciando leitura do ADC e envio UDP..." << std::endl;

    // === Loop principal de leitura e envio ===
    while (true) {
        int valor = sensor.ler();

        if (valor >= 0) {
            std::string msg;

            if (valor > limiar_presenca) {
                msg = "adc," + std::to_string(valor) + ",presenca detectada\n";
                std::cout << ">>> Presenca detectada!" << std::endl;
            } else {
                msg = "adc," + std::to_string(valor) + ",sem presenca\n";
                std::cout << "Sem presenca." << std::endl;
            }

            // Envia mensagem CSV via UDP
            ssize_t enviado = sendto(sock, msg.c_str(), msg.size(), 0,
                                     (sockaddr*)&servidorPC, sizeof(servidorPC));

            if (enviado < 0)
                perror("Erro ao enviar dados via UDP");

            // Exibe valor no terminal local
            std::cout << "Valor ADC: " << valor
                      << " (enviado: " << msg << ")" << std::endl;
        } else {
            std::cerr << "Falha na leitura do ADC." << std::endl;
        }

        // Intervalo entre leituras
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    close(sock); ///< Fecha o socket (nunca alcançado neste loop).
    return 0;
}
