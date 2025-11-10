## @file servidor_udp_gui.py
#  @brief Servidor UDP com interface gráfica Tkinter para visualização em tempo real.
#
#  Este programa cria um servidor UDP que recebe pacotes de um dispositivo remoto
#  e exibe os dados recebidos em uma interface gráfica. Além do texto das mensagens,
#  também mostra um gráfico em tempo real com os valores numéricos recebidos.
#
#  @author Eduardo
#  @date 2025
#  @version 2.0

import socket
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import time

## @brief Classe principal da interface gráfica do servidor UDP.
class ServidorUDPApp:
    def __init__(self, master):
        self.master = master
        master.title("Servidor UDP - Monitor de Sensores")
        master.geometry("800x500")
        master.configure(bg="#1b1b1b")

        # --- Variáveis de rede ---
        self.IP_LOCAL = "192.168.42.10"   
        self.PORTA = 5000
        self.executando = False
        self.socket_udp = None

        # --- Fila para comunicação entre threads ---
        self.queue = queue.Queue()

        # --- Lista de valores recebidos (para o gráfico) ---
        self.valores = []

        # --- Interface visual ---
        self._montar_interface()

        # --- Atualização periódica da interface ---
        self._atualizar_interface()

    def _montar_interface(self):
        # Título
        titulo = tk.Label(
            self.master,
            text="Servidor UDP - Leitura de Sensores",
            font=("Segoe UI", 18, "bold"),
            fg="#00ff88",
            bg="#1b1b1b",
        )
        titulo.pack(pady=10)

        # Frame de botões
        frame_botoes = tk.Frame(self.master, bg="#1b1b1b")
        frame_botoes.pack(pady=5)

        self.botao_iniciar = ttk.Button(frame_botoes, text="Iniciar Servidor", command=self.iniciar_servidor)
        self.botao_iniciar.grid(row=0, column=0, padx=10)

        self.botao_parar = ttk.Button(frame_botoes, text="Parar Servidor", command=self.parar_servidor, state="disabled")
        self.botao_parar.grid(row=0, column=1, padx=10)

        # Campo de texto para logs
        frame_texto = tk.Frame(self.master, bg="#1b1b1b")
        frame_texto.pack(pady=5, fill="both", expand=True)

        self.texto_logs = tk.Text(frame_texto, height=10, bg="#101010", fg="#00ffcc", font=("Consolas", 11))
        self.texto_logs.pack(fill="both", expand=True, padx=15, pady=10)

        # --- Gráfico Matplotlib embutido ---
        frame_grafico = tk.Frame(self.master, bg="#1b1b1b")
        frame_grafico.pack(pady=10, fill="both", expand=True)

        fig = Figure(figsize=(6, 2.5), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor("#202020")
        self.ax.set_title("Valores do Sensor (Tempo Real)", color="white")
        self.ax.set_xlabel("Pacotes")
        self.ax.set_ylabel("Valor")
        self.ax.tick_params(colors="white")
        fig.patch.set_facecolor("#1b1b1b")

        self.line, = self.ax.plot([], [], color="#00ff88", linewidth=2)
        self.canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10)

    ## @brief Inicia o servidor UDP em uma thread separada.
    def iniciar_servidor(self):
        self.executando = True
        self.botao_iniciar.config(state="disabled")
        self.botao_parar.config(state="normal")

        thread = threading.Thread(target=self._rodar_servidor, daemon=True)
        thread.start()

        self._adicionar_log(f"Servidor iniciado em {self.IP_LOCAL}:{self.PORTA}\n")

    ## @brief Para o servidor e fecha o socket.
    def parar_servidor(self):
        self.executando = False
        if self.socket_udp:
            self.socket_udp.close()
        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")
        self._adicionar_log("Servidor encerrado.\n")

    ## @brief Função interna que roda o servidor UDP (em thread separada).
    def _rodar_servidor(self):
        try:
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_udp.bind((self.IP_LOCAL, self.PORTA))

            while self.executando:
                try:
                    self.socket_udp.settimeout(1.0)
                    data, endereco = self.socket_udp.recvfrom(1024)
                    mensagem = data.decode(errors="ignore").strip()

                    # Adiciona a mensagem à fila
                    self.queue.put(mensagem)

                except socket.timeout:
                    continue

        except Exception as e:
            self._adicionar_log(f"Erro no servidor: {e}\n")
        finally:
            if self.socket_udp:
                self.socket_udp.close()

    ## @brief Atualiza a interface periodicamente com novos dados recebidos.
    def _atualizar_interface(self):
        try:
            while not self.queue.empty():
                mensagem = self.queue.get()

                # Exibe a mensagem
                self._adicionar_log(f"{mensagem}\n")

                # Se a mensagem tiver o formato CSV, tenta extrair valor numérico
                partes = mensagem.split(",")
                if len(partes) >= 2:
                    try:
                        valor = float(partes[1])
                        self.valores.append(valor)
                        if len(self.valores) > 50:
                            self.valores.pop(0)
                        self._atualizar_grafico()
                    except ValueError:
                        pass
        except Exception as e:
            self._adicionar_log(f"Erro de interface: {e}\n")

        # Atualiza a cada 200 ms
        self.master.after(200, self._atualizar_interface)

    ## @brief Adiciona texto colorido no campo de logs.
    def _adicionar_log(self, texto):
        self.texto_logs.insert(tk.END, texto)
        self.texto_logs.see(tk.END)

    ## @brief Atualiza o gráfico com novos valores.
    def _atualizar_grafico(self):
        self.line.set_data(range(len(self.valores)), self.valores)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()


## @brief Ponto de entrada principal do programa.
if __name__ == "__main__":
    root = tk.Tk()
    estilo = ttk.Style()
    estilo.theme_use("clam")
    app = ServidorUDPApp(root)
    root.mainloop()
