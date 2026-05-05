import subprocess
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk

class CopiadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Copiador da Tammy")
        self.root.geometry("650x680")
        self.root.configure(bg="#ffffff")
        
        # Tema clean
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuração de cores e fontes
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#ffffff", font=("Segoe UI", 16, "bold"), foreground="#333333")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Normal.TButton", font=("Segoe UI", 9), padding=4)
        style.configure("TProgressbar", thickness=15)
        style.configure("TCheckbutton", background="#ffffff", font=("Segoe UI", 10))
        
        self.is_copying = False
        self.create_widgets()

    def get_adb_path(self):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, 'adb.exe')
        return "adb"

    def create_widgets(self):
        # --- Título ---
        ttk.Label(self.root, text="Copiador da Tammy", style="Header.TLabel").pack(pady=(25, 15))

        # --- Área de Configurações ---
        frame_config = ttk.Frame(self.root)
        frame_config.pack(fill=tk.X, padx=30, pady=10)

        # Pasta Celular
        ttk.Label(frame_config, text="Origem (Celular):").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.entry_celular = ttk.Entry(frame_config, width=45, font=("Segoe UI", 10))
        self.entry_celular.insert(0, "/sdcard/DCIM")
        self.entry_celular.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        
        btn_browse_cel = ttk.Button(frame_config, text="Procurar...", style="Normal.TButton", command=self.browse_celular_folder)
        btn_browse_cel.grid(row=0, column=2, padx=5, pady=10)

        # Pasta PC
        ttk.Label(frame_config, text="Destino (PC):").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_pc = ttk.Entry(frame_config, width=45, font=("Segoe UI", 10))
        self.entry_pc.insert(0, r"C:\Fotos_Backup")
        self.entry_pc.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        
        btn_browse_pc = ttk.Button(frame_config, text="Procurar...", style="Normal.TButton", command=self.browse_pc_folder)
        btn_browse_pc.grid(row=1, column=2, padx=5, pady=10)
        
        frame_config.columnconfigure(1, weight=1)

        # --- Opções Adicionais ---
        frame_opcoes = ttk.Frame(self.root)
        frame_opcoes.pack(fill=tk.X, padx=30, pady=5)
        
        self.var_mover = tk.BooleanVar(value=False)
        chk_mover = ttk.Checkbutton(frame_opcoes, text=" Mover arquivos (Apagar do celular após transferir para liberar espaço)", variable=self.var_mover, style="TCheckbutton")
        chk_mover.pack(side=tk.LEFT)

        btn_wifi = ttk.Button(frame_opcoes, text="📡 Conectar Wi-Fi", style="Normal.TButton", command=self.conectar_wifi)
        btn_wifi.pack(side=tk.RIGHT)

        # --- Botão Iniciar ---
        self.btn_iniciar = ttk.Button(self.root, text="▶ INICIAR TRANSFERÊNCIA", style="Action.TButton", command=self.iniciar_copia)
        self.btn_iniciar.pack(pady=(15, 20))

        # --- Progresso ---
        frame_progress = ttk.Frame(self.root)
        frame_progress.pack(fill=tk.X, padx=30)
        
        self.lbl_status = ttk.Label(frame_progress, text="Pronto para iniciar.", foreground="#666666")
        self.lbl_status.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_progress, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)

        # --- Log Visual ---
        frame_log = ttk.Frame(self.root)
        frame_log.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        self.log_area = scrolledtext.ScrolledText(
            frame_log, 
            height=10, 
            state='disabled', 
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#212529",
            relief=tk.FLAT,
            borderwidth=1
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def browse_pc_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_pc.delete(0, tk.END)
            self.entry_pc.insert(0, os.path.normpath(folder))

    def browse_celular_folder(self):
        if not self.executar_comando([self.get_adb_path(), "devices"]) or "device\n" not in self.executar_comando([self.get_adb_path(), "devices"]):
            messagebox.showwarning("Aviso", "O celular não foi detectado.\n\nVerifique o cabo e se a 'Depuração USB' está ativa.")
            return

        top = tk.Toplevel(self.root)
        top.title("Navegador do Celular")
        top.geometry("400x500")
        top.configure(bg="#ffffff")
        top.transient(self.root)
        top.grab_set()

        ttk.Label(top, text="Selecione a pasta no celular:", font=("Segoe UI", 11, "bold")).pack(pady=(15, 5))

        path_var = tk.StringVar(value="/sdcard")
        ttk.Label(top, textvariable=path_var, font=("Consolas", 10), foreground="#0056b3").pack(pady=5)

        frame_list = tk.Frame(top, bg="#e9ecef", padx=1, pady=1)
        frame_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        listbox = tk.Listbox(frame_list, font=("Segoe UI", 10), selectmode=tk.SINGLE, relief=tk.FLAT, bg="#ffffff", highlightthickness=0)
        listbox.pack(fill=tk.BOTH, expand=True)

        def carregar_pasta(path):
            listbox.delete(0, tk.END)
            listbox.insert(tk.END, "📁 .. (Subir)")
            
            cmd = [self.get_adb_path(), "shell", f"ls -1 '{path}/'"]
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=creationflags)
                if res.returncode == 0:
                    items = [i.strip().replace('\r', '') for i in res.stdout.split('\n') if i.strip()]
                    for item in items:
                        if item and not item.startswith("ls:") and not item.endswith("No such file or directory"):
                            listbox.insert(tk.END, "📁 " + item)
            except Exception:
                pass

        carregar_pasta(path_var.get())

        def on_double_click(event):
            selection = listbox.curselection()
            if not selection: return
            item = listbox.get(selection[0]).replace("📁 ", "")
            
            curr = path_var.get()
            if item == ".. (Subir)":
                if curr not in ["/", "/sdcard"]:
                    novo_path = os.path.dirname(curr)
                    path_var.set(novo_path if novo_path != "/" else "/")
                    carregar_pasta(path_var.get())
            else:
                novo_path = f"{curr}/{item}" if curr != "/" else f"/{item}"
                cmd = [self.get_adb_path(), "shell", f"ls '{novo_path}/'"]
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=creationflags)
                if "Not a directory" not in res.stderr and "Not a directory" not in res.stdout:
                    path_var.set(novo_path)
                    carregar_pasta(novo_path)

        listbox.bind("<Double-1>", on_double_click)

        def confirmar():
            self.entry_celular.delete(0, tk.END)
            self.entry_celular.insert(0, path_var.get())
            top.destroy()

        ttk.Button(top, text="Confirmar Pasta", style="Action.TButton", command=confirmar).pack(pady=15)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def conectar_wifi(self):
        top = tk.Toplevel(self.root)
        top.title("Conexão Wi-Fi (ADB)")
        top.geometry("450x250")
        top.configure(bg="#ffffff")
        top.transient(self.root)
        top.grab_set()
        
        ttk.Label(top, text="1. Ative a 'Depuração sem fio' nas Opções de Desenvolvedor.\n2. Digite abaixo o Endereço IP e Porta exibidos lá no celular.", justify=tk.CENTER, font=("Segoe UI", 10)).pack(pady=20)
        
        frame_ip = tk.Frame(top, bg="#ffffff")
        frame_ip.pack(pady=5)
        ttk.Label(frame_ip, text="IP:Porta -> ", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        entry_ip = ttk.Entry(frame_ip, width=22, font=("Segoe UI", 10))
        entry_ip.pack(side=tk.LEFT)
        entry_ip.insert(0, "192.168.0.x:5555")
        
        def fazer_conexao():
            endereco = entry_ip.get().strip()
            self.log(f"Tentando conectar via Wi-Fi ({endereco})...")
            top.destroy()
            def run_connect():
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                res = subprocess.run([self.get_adb_path(), "connect", endereco], capture_output=True, text=True, creationflags=creationflags)
                if "connected" in res.stdout.lower() and "failed" not in res.stdout.lower():
                    self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Celular conectado via Wi-Fi!\nAgora você pode remover o cabo e realizar a cópia."))
                    self.root.after(0, lambda: self.log("✅ Conectado via Wi-Fi com sucesso! O cabo já pode ser removido."))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Erro", f"Falha na conexão. Verifique se o IP e Porta estão corretos e na mesma rede Wi-Fi.\n\nDetalhes:\n{res.stdout}"))
            threading.Thread(target=run_connect, daemon=True).start()
            
        ttk.Button(top, text="Conectar", style="Action.TButton", command=fazer_conexao).pack(pady=20)

    def executar_comando(self, comando):
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True, encoding='utf-8', creationflags=creationflags)
            return resultado.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return "ERRO_ADB_NAO_ENCONTRADO"

    def iniciar_copia(self):
        if self.is_copying: return
            
        pasta_celular = self.entry_celular.get().strip()
        pasta_pc = self.entry_pc.get().strip()
        mover_arquivos = self.var_mover.get()
        
        if not pasta_celular or not pasta_pc:
            messagebox.showwarning("Aviso", "Preencha a origem e o destino.")
            return
            
        if mover_arquivos:
            resposta = messagebox.askyesno("Aviso de Exclusão", "Você marcou a opção de MOVER os arquivos.\n\nIsso significa que as fotos e vídeos serão APAGADOS do celular assim que chegarem no PC para liberar espaço.\n\nTem certeza que deseja continuar?")
            if not resposta:
                return

        self.btn_iniciar.config(state=tk.DISABLED)
        self.is_copying = True
        
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
        self.progress_var.set(0)
        self.lbl_status.config(text="Iniciando...", foreground="#333333")
        
        threading.Thread(target=self.processo_copia, args=(pasta_celular, pasta_pc, mover_arquivos), daemon=True).start()

    def processo_copia(self, pasta_celular, pasta_pc, mover_arquivos):
        self.root.after(0, lambda: self.log("Testando conexão..."))
        dispositivos = self.executar_comando([self.get_adb_path(), "devices"])
        
        if dispositivos == "ERRO_ADB_NAO_ENCONTRADO":
            self.root.after(0, lambda: self.log("ERRO: O ADB não foi encontrado internamente."))
            self.root.after(0, self.finalizar_copia)
            return
            
        if not dispositivos or "device" not in dispositivos.replace("List of devices attached", ""):
            self.root.after(0, lambda: self.log("ERRO: Nenhum celular detectado.\nAtive a 'Depuração USB' nas opções de desenvolvedor do Android."))
            self.root.after(0, self.finalizar_copia)
            return

        self.root.after(0, lambda: self.log(f"Lendo arquivos de {pasta_celular} (isso pode demorar)..."))
        saida = self.executar_comando([self.get_adb_path(), "shell", "find", f'"{pasta_celular}"', "-type", "f"])
        
        if not saida:
            self.root.after(0, lambda: self.log("Nenhum arquivo encontrado na pasta ou acesso negado."))
            self.root.after(0, self.finalizar_copia)
            return
            
        arquivos = [linha.strip().replace('\r', '') for linha in saida.split('\n') if linha.strip()]
        total_arquivos = len(arquivos)
        
        self.root.after(0, lambda: self.log(f"Encontrados {total_arquivos} arquivos.\n"))
        
        copiados = ignorados = erros = 0
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        for index, caminho_remoto in enumerate(arquivos):
            if not self.is_copying: break
                
            caminho_remoto_limpo = caminho_remoto.replace('"', '')
            caminho_relativo = caminho_remoto_limpo.replace(pasta_celular + "/", "")
            caminho_relativo_windows = caminho_relativo.replace("/", os.sep)
            caminho_local = os.path.join(pasta_pc, caminho_relativo_windows)
            
            os.makedirs(os.path.dirname(caminho_local), exist_ok=True)
            
            progresso_percentual = ((index + 1) / total_arquivos) * 100
            self.root.after(0, lambda p=progresso_percentual, f=caminho_relativo: self.atualizar_interface(p, f))
            
            if os.path.exists(caminho_local):
                ignorados += 1
                self.root.after(0, lambda msg=f"Pulando (já existe): {caminho_relativo}": self.log(msg))
                
                if mover_arquivos:
                    subprocess.run([self.get_adb_path(), "shell", f'rm "{caminho_remoto_limpo}"'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
                continue
                
            self.root.after(0, lambda msg=f"{'Movendo' if mover_arquivos else 'Copiando'}: {caminho_relativo}": self.log(msg))
            
            caminho_local_temp = caminho_local + ".tmp"
            try:
                subprocess.run([self.get_adb_path(), "pull", caminho_remoto_limpo, caminho_local_temp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=creationflags)
                
                if os.path.exists(caminho_local_temp):
                    os.replace(caminho_local_temp, caminho_local)
                
                copiados += 1
                
                if mover_arquivos:
                    subprocess.run([self.get_adb_path(), "shell", f'rm "{caminho_remoto_limpo}"'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
                    
            except subprocess.CalledProcessError:
                self.root.after(0, lambda msg=f"  -> ERRO: {caminho_relativo}": self.log(msg))
                erros += 1

        acao_str = "Movidos" if mover_arquivos else "Copiados"
        resumo = f"\n=== CONCLUÍDO ===\n{acao_str} agora: {copiados}\nPulados (já existiam): {ignorados}\nErros: {erros}"
        self.root.after(0, lambda: self.log(resumo))
        self.root.after(0, self.finalizar_copia)

    def atualizar_interface(self, percentual, nome_arquivo):
        self.progress_var.set(percentual)
        if len(nome_arquivo) > 65:
            nome_arquivo = "..." + nome_arquivo[-62:]
        self.lbl_status.config(text=f"[{int(percentual)}%] Processando: {nome_arquivo}", foreground="#0056b3")

    def finalizar_copia(self):
        self.is_copying = False
        self.btn_iniciar.config(state=tk.NORMAL)
        if self.progress_var.get() > 0:
            self.progress_var.set(100)
            self.lbl_status.config(text="Processo concluído!", foreground="#28a745")

if __name__ == "__main__":
    root = tk.Tk()
    app = CopiadorApp(root)
    root.mainloop()
