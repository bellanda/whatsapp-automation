import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from utilities.whatsapp import WhatsAppAutomation


class WhatsAppAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Automação")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.automation = None
        self.thread = None
        self.is_running = False

        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, text="WhatsApp Automação", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Frame para o seletor de arquivo
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)

        self.file_path_var = tk.StringVar()

        file_label = ttk.Label(file_frame, text="Arquivo JSON:")
        file_label.pack(side=tk.LEFT, padx=(0, 10))

        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        browse_button = ttk.Button(file_frame, text="Procurar", command=self.browse_file)
        browse_button.pack(side=tk.LEFT)

        # Frame para as opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        self.reset_var = tk.BooleanVar(value=False)
        reset_check = ttk.Checkbutton(options_frame, text="Recomeçar do zero (ignorar progresso)", variable=self.reset_var)
        reset_check.pack(fill=tk.X)

        # Frame para status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.status_text.config(yscrollcommand=scrollbar.set)

        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(button_frame, text="Iniciar Automação", command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo JSON", filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )

        if file_path:
            self.file_path_var.set(file_path)
            self.update_status(f"Arquivo selecionado: {file_path}")

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_automation(self):
        file_path = self.file_path_var.get()

        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo JSON primeiro!")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("Erro", "O arquivo selecionado não existe!")
            return

        # Desabilitar o botão de iniciar e habilitar o de parar
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Limpar a caixa de status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)

        # Iniciar a automação em uma thread separada
        self.is_running = True
        self.thread = threading.Thread(target=self._run_automation, args=(file_path,))
        self.thread.daemon = True
        self.thread.start()

    def _run_automation(self, file_path):
        try:
            self.update_status("Iniciando automação...")

            # Criar a instância de automação
            self.automation = WhatsAppAutomation(file_path)

            # Resetar progresso se solicitado
            if self.reset_var.get():
                self.update_status("Resetando progresso anterior...")
                self.automation.reset_progress()

            # Carregar contatos
            self.update_status("Carregando contatos do arquivo JSON...")
            if not self.automation.load_contacts():
                self.update_status("Erro ao carregar contatos do arquivo JSON!")
                self._finish_automation()
                return

            self.update_status(f"Foram encontrados {len(self.automation.contacts)} contatos no arquivo JSON.")

            # Verificar se todos os contatos já foram processados
            if self.automation.all_contacts_processed():
                self.update_status("Todos os contatos já foram processados. Nada a enviar.")
                self._finish_automation()
                return

            # Inicializar o driver (não é mais necessário chamar explicitamente, pois agora send_messages faz isso)
            self.update_status("Inicializando o navegador...")

            # Enviar mensagens
            self.update_status("Iniciando envio de mensagens. Por favor, aguarde...")
            self.automation.send_messages(self.update_status)

            self.update_status("Automação concluída com sucesso!")

        except Exception as e:
            self.update_status(f"Erro durante a automação: {e}")

        finally:
            # Fechar o driver
            if self.automation:
                self.automation.close()

            self._finish_automation()

    def stop_automation(self):
        if self.is_running:
            self.is_running = False
            self.update_status("Parando automação...")

            if self.automation:
                self.automation.close()

            self._finish_automation()

    def _finish_automation(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
