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

##  Estrutura do Código Main

- **Classe `LerADC`**  
  Responsável por abrir o arquivo de leitura do canal ADC (`/sys/bus/iio/devices/iio:device0/in_voltageX_raw`) e retornar o valor lido.

- **Loop principal (`main`)**  
  - Cria o socket UDP.  
  - Configura o endereço IP e a porta do PC destino.  
  - Lê o ADC a cada 2 segundos.  
  - Envia os dados para o PC.  
  - Exibe no terminal se houve **presença detectada**.


  ## Estrutura e Funcionamento do Código Python

O código em Python é responsável pela **leitura da tensão enviada pela placa microcontroladora** e pelo **acionamento de uma luz indicativa (LED virtual)** dependendo do valor medido. Ele se comunica com o hardware via **UDP** e exibe informações de status em tempo real.

###  Lógica Principal

1. O código recebe continuamente os dados de tensão vindos pela rede.
2. Ele converte o valor recebido para número e verifica se a tensão ultrapassa um limite predefinido.
3. Caso a tensão atinja um valor muito alto (por exemplo, acima de `50000`), a luz virtual muda para **verde**, indicando que a condição foi atingida.
4. Caso contrário, a luz permanece em outra cor (por exemplo, vermelha), indicando nível normal.

###  Estrutura do Código

- **Importação de bibliotecas**: inclui os módulos necessários para comunicação via rede e interface gráfica.
- **Configuração do socket UDP**: define o IP e a porta usados na comunicação com a placa.
- **Função principal (`main`)**:
  - Recebe os dados de tensão.
  - Processa o valor.
  - Atualiza a cor da luz conforme o nível de tensão.
- **Interface gráfica (Tkinter)**:
  - Exibe a luz (LED virtual).
  - Atualiza sua cor dinamicamente conforme os dados recebidos.

###  Exemplo de Funcionamento

Quando a placa envia um pacote UDP com a tensão:

```python
tensao = 52340
```

O código identifica que o valor é alto e muda o LED para **verde**, sinalizando o evento.

###  Organização Recomendada

```
Projeto_Sensor_AM312/
│
├── main.cpp              # Código principal da aplicação em C++
├── server.py             # Código Python responsável pela interface e leitura via UDP
├── Doxyfile              # Arquivo de configuração do Doxygen
├── docs/                 # Documentação gerada automaticamente pelo Doxygen
└── README.md             # Descrição geral do projeto
```

###  Integração com o Sistema

O código Python complementa o `main.cpp` fornecendo:
- Uma **interface gráfica simples** para visualização dos dados.
- Um **mecanismo de comunicação UDP** que permite o envio e recebimento de informações entre o microcontrolador e o sistema principal.



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

## Abrindo a interface:
Essas mensagens UDP vão chegar para a interface gráfica. Para abrir ela sem ter que abrir o código fonte, você pode gerar um executável empacotado. Para isso, basta instalar o pyinstaller pelo terminal:
```pip install pyinstaller```

Após isso, basta digitar:
```pyinstaller --onefile --windowed server.py```
Onde 
--onefile: cria um único arquivo .exe (ou binário Linux).

--windowed: impede que o terminal apareça junto com a interface gráfica (Tkinter).

Depois disso, teremos nosso executável server.exe.



