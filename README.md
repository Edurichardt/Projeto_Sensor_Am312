# Projeto: Leitura de ADC e Envio via UDP (STM32 + AM312)

Este projeto tem como objetivo **ler valores analógicos** de um canal ADC em uma placa **STM32** e enviar periodicamente esses valores para um PC remoto via **UDP**.  
O sensor utilizado é o **AM312 (sensor PIR de presença)**, conectado a um canal ADC da placa.

---

## Funcionalidades

- Leitura periódica do valor analógico do ADC (via interface **IIO** do Linux embarcado).
- Envio dos valores para um PC remoto no formato **CSV** (`adc,<valor>`).
- Exibição dos valores no terminal.
- Detecção de presença com base em um limiar configurável.

---

##  Estrutura do Código

- **Classe `LerADC`**  
  Responsável por abrir o arquivo de leitura do canal ADC (`/sys/bus/iio/devices/iio:device0/in_voltageX_raw`) e retornar o valor lido.

- **Loop principal (`main`)**  
  - Cria o socket UDP.  
  - Configura o endereço IP e a porta do PC destino.  
  - Lê o ADC a cada 2 segundos.  
  - Envia os dados para o PC.  
  - Exibe no terminal se houve **presença detectada**.


## Compilação Cruzada para o Linux Embarcado (STM32)
Como a placa STM32 roda um Linux embarcado, o código deve ser compilado cruzado em uma máquina virtual Linux e depois transferido para a placa.

1. Na máquina virtual Linux:
-  Instale a toolchain:

```tar -xvf arm-buildroot-linux-gnueabihf_sdk-DK2.tar.gz```

-  Escreva o código e salve como cpp 
```nano```

```projeto.cpp```
-  Compile com a toolchain
```arm-linux-gnueabihf-g++ projeto.cpp -o projeto -pthread```

2. Transferir o binário para a placa através de uma pasta compartilhada

3. Acessar a placa via SSH:
-  No PowerShell do Windows:
```ssh root@<ip_da_placa>```
- Depois digite a senha e pronto, estará dentro do sistema da placa

4. Executar o programa na placa:
-  Depois de acessar via SSH:
```chmod +x adc_udp```
```./projeto```

Canal ADC
- Para saber qual o canal, basta conectar a saída ADC da placa ao GND dela e digitar os seguintes comandos no terminal da placa:
```cd /sys/bus/iio/devices/iio:device0/```
```ls```
-  Vai listar os arquivos e vão aparecer arquivos do tipo in_voltageX_raw, sendo x um número. Agora, basta digitar:
```cat in_voltageX_raw```
-  O que der zero será a saída correta a ser utilizada (no meu caso foi a saída 13)

```int canal_adc = 13;```
Esse número deve corresponder ao canal utilizado no STM32 .


## Abrindo Porta no Firewall do Windows

Para que o PC consiga receber os pacotes UDP enviados pela placa, é necessário liberar a porta utilizada (ex.: `5000`) no **Firewall do Windows**.

### Passos:

1. Abra o menu **Iniciar** e pesquise por **"Firewall do Windows com Segurança Avançada"**.
2. No painel à esquerda, clique em **Regras de Entrada**.
3. No painel à direita, clique em **Nova Regra...**.
4. Selecione **Porta** e avance.
5. Escolha **UDP** e insira a porta desejada (ex.: `5000`).
6. Clique em **Permitir a conexão** e avance.
7. Marque todos os perfis (Domínio, Privado, Público).
8. Dê um nome à regra (ex.: `UDP Porta 5000`) e conclua.

Agora o PC poderá receber mensagens UDP nessa porta.



