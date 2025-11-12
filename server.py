## @file servidor_udp_interface.py
#  @brief Interface gráfica em Tkinter para recepção e exibição de dados UDP em tempo real.
#
#  Este script implementa um servidor UDP que recebe mensagens de um dispositivo remoto
#  (como uma placa com sensor) e exibe as informações em uma interface visual.
#  Quando o valor recebido ultrapassa um limiar configurável, a interface indica presença
#  com uma luz verde; caso contrário, permanece vermelha.
#
#  O sistema usa multithreading para garantir que a recepção de pacotes UDP não
#  bloqueie a atualização da interface gráfica.
#
#  @author Eduardo
#  @date 2025
#  @version 1.0

import socket
import threading
import tkinter as tk
from tkinter import ttk
import queue


## @class ServidorUDPApp
#  @brief Classe principal da aplicação Tkinter para o servidor UDP.
#
#  Esta classe cria a janela gráfica, inicializa o servidor UDP em uma thread separada,
#  e atualiza continuamente a interface conforme os dados recebidos.
class ServidorUDPApp:
    ## @brief Construtor da classe ServidorUDPApp.
    #  @param master A janela principal do Tkinter.
    def __init__(self, master):
        self.master = master
        master.title("Servidor UDP - Indicador de Presença")
        master.geometry("600x400")
        master.configure(bg="#1b1b1b")

        ## @var IP_LOCAL
        #  Endereço IP local em que o servidor UDP irá escutar.
        self.IP_LOCAL = "192.168.42.10"

        ## @var PORTA
        #  Porta UDP utilizada para receber os pacotes de dados.
        self.PORTA = 5000

        ## @var executando
        #  Indica se o servidor está ativo (True) ou parado (False).
        self.executando = False

        ## @var socket_udp
        #  Objeto socket utilizado para comunicação UDP.
        self.socket_udp = None

        ## @var queue
        #  Fila de mensagens usada para troca segura entre threads.
        self.queue = queue.Queue()

        ## @var limiar_presenca
        #  Valor mínimo do sensor para ser considerado "presença detectada".
        self.limiar_presenca = 50000

        ## @brief Monta todos os elementos da interface gráfica.
        self._montar_interface()

        ## @brief Inicia o loop de atualização da interface.
        self._atualizar_interface()

    ## @brief Monta os elementos da interface gráfica.
    def _montar_interface(self):
        titulo = tk.Label(
            self.master,
            text="Servidor UDP - Indicador de Presença",
            font=("Segoe UI", 18, "bold"),
            fg="#00ff88",
            bg="#1b1b1b",
        )
        titulo.pack(pady=10)

        # --- Botões de controle ---
        frame_botoes = tk.Frame(self.master, bg="#1b1b1b")
        frame_botoes.pack(pady=5)

        ## @var botao_iniciar
        #  Botão para iniciar o servidor UDP.
        self.botao_iniciar = ttk.Button(frame_botoes, text="Iniciar Servidor", command=self.iniciar_servidor)
        self.botao_iniciar.grid(row=0, column=0, padx=10)

        ## @var botao_parar
        #  Botão para encerrar o servidor UDP.
        self.botao_parar = ttk.Button(frame_botoes, text="Parar Servidor", command=self.parar_servidor, state="disabled")
        self.botao_parar.grid(row=0, column=1, padx=10)

        # --- Indicador visual de presença ---
        frame_indicador = tk.Frame(self.master, bg="#1b1b1b")
        frame_indicador.pack(pady=20)

        ## @var canvas
        #  Canvas usado para desenhar o círculo indicador de presença.
        self.canvas = tk.Canvas(frame_indicador, width=120, height=120, bg="#1b1b1b", highlightthickness=0)
        self.canvas.pack()

        ## @var indicador
        #  Elemento oval (círculo) que muda de cor conforme o valor do sensor.
        self.indicador = self.canvas.create_oval(10, 10, 110, 110, fill="#ff3333", outline="black", width=2)

        ## @var label_estado
        #  Rótulo textual que indica o estado atual ("Sem presença" ou "Presença detectada").
        self.label_estado = tk.Label(
            frame_indicador,
            text="Sem presença",
            font=("Segoe UI", 14, "bold"),
            fg="#ff5555",
            bg="#1b1b1b",
        )
        self.label_estado.pack(pady=10)

        # --- Caixa de texto de logs ---
        frame_texto = tk.Frame(self.master, bg="#1b1b1b")
        frame_texto.pack(pady=5, fill="both", expand=True)

        ## @var texto_logs
        #  Widget de texto que exibe as mensagens recebidas e logs do sistema.
        self.texto_logs = tk.Text(frame_texto, height=8, bg="#101010", fg="#00ffcc", font=("Consolas", 11))
        self.texto_logs.pack(fill="both", expand=True, padx=15, pady=10)

    ## @brief Inicia o servidor UDP em uma thread separada.
    def iniciar_servidor(self):
        self.executando = True
        self.botao_iniciar.config(state="disabled")
        self.botao_parar.config(state="normal")

        thread = threading.Thread(target=self._rodar_servidor, daemon=True)
        thread.start()

        self._adicionar_log(f"Servidor iniciado em {self.IP_LOCAL}:{self.PORTA}\n")

    ## @brief Interrompe a execução do servidor UDP e fecha o socket.
    def parar_servidor(self):
        self.executando = False
        if self.socket_udp:
            self.socket_udp.close()
        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")
        self._adicionar_log("Servidor encerrado.\n")

    ## @brief Loop principal de recepção de pacotes UDP.
    #
    #  O servidor escuta continuamente por mensagens UDP e as envia
    #  para a fila de mensagens `queue`, onde serão processadas pela interface.
    def _rodar_servidor(self):
        try:
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_udp.bind((self.IP_LOCAL, self.PORTA))

            while self.executando:
                try:
                    self.socket_udp.settimeout(1.0)
                    data, endereco = self.socket_udp.recvfrom(1024)
                    mensagem = data.decode(errors="ignore").strip()
                    self.queue.put(mensagem)
                except socket.timeout:
                    continue
        except Exception as e:
            self._adicionar_log(f"Erro no servidor: {e}\n")
        finally:
            if self.socket_udp:
                self.socket_udp.close()

    ## @brief Atualiza periodicamente a interface com os dados recebidos.
    #
    #  Esta função é chamada a cada 200 ms para verificar a fila de mensagens
    #  e atualizar o log e o indicador visual conforme os valores recebidos.
    def _atualizar_interface(self):
        try:
            while not self.queue.empty():
                mensagem = self.queue.get()
                self._adicionar_log(f"{mensagem}\n")

                partes = mensagem.split(",")
                if len(partes) >= 2:
                    try:
                        valor = float(partes[1])
                        # Atualiza o indicador visual conforme o valor
                        if valor > self.limiar_presenca:
                            self.canvas.itemconfig(self.indicador, fill="#00ff55")
                            self.label_estado.config(text="Presença detectada", fg="#00ff55")
                        else:
                            self.canvas.itemconfig(self.indicador, fill="#ff3333")
                            self.label_estado.config(text="Sem presença", fg="#ff5555")
                    except ValueError:
                        pass
        except Exception as e:
            self._adicionar_log(f"Erro de interface: {e}\n")

        self.master.after(200, self._atualizar_interface)

    ## @brief Adiciona texto à área de logs da interface.
    #  @param texto String contendo a mensagem a ser exibida.
    def _adicionar_log(self, texto):
        self.texto_logs.insert(tk.END, texto)
        self.texto_logs.see(tk.END)



## @brief Ponto de entrada do programa.
#
#  Cria a janela principal, aplica o tema e inicia o loop Tkinter.
if __name__ == "__main__":
    root = tk.Tk()
    estilo = ttk.Style()
    estilo.theme_use("clam")
    app = ServidorUDPApp(root)
    root.mainloop()
