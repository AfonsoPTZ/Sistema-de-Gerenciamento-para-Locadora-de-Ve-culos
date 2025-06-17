import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
# Importa as funções do seu arquivo de banco de dados
# Certifique-se de que este arquivo se chame 'database.py' e esteja na mesma pasta
import database as db

# =============================================================================
# WIDGET PERSONALIZADO COM PLACEHOLDER
# =============================================================================

class EntryComTextoDeAjuda(ttk.Entry):
    """Um widget de entrada de texto que exibe um texto de ajuda quando vazio."""
    def __init__(self, master=None, texto_ajuda="PLACEHOLDER", cor_texto_ajuda='grey', **kwargs):
        super().__init__(master, **kwargs)

        self.texto_ajuda = texto_ajuda
        self.cor_texto_ajuda = cor_texto_ajuda
        self.cor_padrao_texto = self['foreground']
        self.mostrando_texto_ajuda = False 

        self.bind("<FocusIn>", self._ao_receber_foco)
        self.bind("<FocusOut>", self._ao_perder_foco)

        self._colocar_texto_ajuda()

    def _colocar_texto_ajuda(self):
        if not self.get():
            self.delete(0, tk.END)
            self.insert(0, self.texto_ajuda)
            self['foreground'] = self.cor_texto_ajuda
            self.mostrando_texto_ajuda = True

    def _ao_receber_foco(self, *args):
        if self.mostrando_texto_ajuda:
            self.delete('0', 'end')
            self['foreground'] = self.cor_padrao_texto
            self.mostrando_texto_ajuda = False

    def _ao_perder_foco(self, *args):
        if not self.get():
            self._colocar_texto_ajuda()
        else:
            self.mostrando_texto_ajuda = False

# =============================================================================
# FUNÇÕES AUXILIARES DE FORMATAÇÃO E UI
# =============================================================================

def criar_cabecalho_secao(parent, text):
    frame_cabecalho = ttk.Frame(parent)
    frame_cabecalho.pack(fill="x", padx=10, pady=(15, 5))
    frame_cabecalho.columnconfigure(0, weight=1)
    frame_cabecalho.columnconfigure(2, weight=1)

    ttk.Separator(frame_cabecalho, orient="horizontal").grid(row=0, column=0, sticky="ew", padx=10)
    ttk.Label(
        frame_cabecalho,
        text=text,
        font=("Arial", 14, "bold"),
        anchor="center"
    ).grid(row=0, column=1, sticky="ew", padx=10)
    ttk.Separator(frame_cabecalho, orient="horizontal").grid(row=0, column=2, sticky="ew", padx=10)

def formatar_cpf(cpf):
    cpf_numerico = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf_numerico) == 11:
        return f"{cpf_numerico[:3]}.{cpf_numerico[3:6]}.{cpf_numerico[6:9]}-{cpf_numerico[9:]}"
    return cpf

def formatar_telefone(telefone):
    tel_numerico = ''.join(filter(str.isdigit, str(telefone)))
    if len(tel_numerico) == 11:
        return f"({tel_numerico[:2]}) {tel_numerico[2:7]}-{tel_numerico[7:]}"
    if len(tel_numerico) == 10:
        return f"({tel_numerico[:2]}) {tel_numerico[2:6]}-{tel_numerico[6:]}"
    return telefone

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

def formatar_texto_capitalizado(texto):
    if isinstance(texto, str):
        return texto.title()
    return texto

def obter_cabecalho_exibicao(nome_coluna):
    cabecalhos = {
        "cpf": "CPF", "valor_diaria": "Valor da Diária", "email": "E-mail",
        "id": "ID", "placa_carro": "Placa do Carro", "cpf_cliente": "CPF do Cliente",
        "data_retirada": "Data de Retirada", "data_devolucao": "Data de Devolução",
        "nome_cliente": "Nome do Cliente", "valor_total": "Valor Total", "carro": "Carro",
        "cliente": "Cliente", "data_entrada": "Data de Entrada", "data_saida": "Data de Saída",
        "custo": "Custo Previsto", "descricao": "Descrição"
    }
    return cabecalhos.get(nome_coluna, nome_coluna.replace("_", " ").title())

# =============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# =============================================================================

class LocadoraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento de Locadora")
        self.geometry("1200x750")

        db.criar_tabelas()

        self._configurar_estilos()
        self._criar_widgets_principais()
        
        self.focus_set()
        self.ao_mudar_aba(None)

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Emoji.TButton", font=("Arial", 11), padding=5, anchor="center")
        style.configure("TLabelFrame.Label", font=("Arial", 12, "bold"))
        style.configure('TNotebook.Tab', font=('Arial','10', 'bold'), padding=[10, 4])

    def _criar_widgets_principais(self):
        titulo_label = ttk.Label(self, text="🚗\u2009Sistema de Locadora de Veículos", font=("Arial", 18, "bold"), anchor="center")
        titulo_label.pack(pady=(10, 5), fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=5, padx=10, expand=True, fill="both")

        self.tab_veiculos = AbaVeiculos(self.notebook)
        self.tab_clientes = AbaClientes(self.notebook)
        self.tab_alugueis = AbaAlugueis(self.notebook)
        self.tab_manutencao = AbaManutencao(self.notebook)
        self.tab_relatorios = AbaRelatorios(self.notebook)

        self.notebook.add(self.tab_veiculos, text="🚗\u2009Veículos")
        self.notebook.add(self.tab_clientes, text="👥\u2009Clientes")
        self.notebook.add(self.tab_alugueis, text="🔑\u2009Aluguéis")
        self.notebook.add(self.tab_manutencao, text="🛠️\u2009Manutenção")
        self.notebook.add(self.tab_relatorios, text="📊\u2009Relatórios")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.ao_mudar_aba)

    def ao_mudar_aba(self, event):
        self.focus_set()
        try:
            aba_selecionada = self.notebook.select()
            nome_da_aba = self.notebook.tab(aba_selecionada, "text")

            if "Veículos" in nome_da_aba:
                self.tab_veiculos.popular_lista_veiculos()
            elif "Clientes" in nome_da_aba:
                self.tab_clientes.popular_lista_clientes()
            elif "Aluguéis" in nome_da_aba:
                self.tab_alugueis.popular_alugueis_ativos()
                self.tab_alugueis.atualizar_sugestoes()
            elif "Manutenção" in nome_da_aba:
                self.tab_manutencao.popular_manutencoes_ativas()
                self.tab_manutencao.atualizar_veiculos_disponiveis()
            elif "Relatórios" in nome_da_aba:
                self.tab_relatorios.ver_historico_geral()
                self.tab_relatorios.atualizar_sugestoes_cpf()
        except tk.TclError:
            pass

# =============================================================================
# ABA DE VEÍCULOS
# =============================================================================

class AbaVeiculos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.item_selecionado = None
        self._criar_widgets()
        self.popular_lista_veiculos()

    def _criar_widgets(self):
        criar_cabecalho_secao(self, "Cadastro de Veículo")
        frame_formulario_wrapper = ttk.Frame(self)
        frame_formulario_wrapper.pack(pady=(0, 10))
        frame_formulario = ttk.Frame(frame_formulario_wrapper)
        frame_formulario.pack()
        
        campos = {
            "Placa:": "ABC-1234 ou ABC1D23", "Marca:": "Ex: Toyota", "Modelo:": "Ex: Corolla",
            "Ano:": "Ex: 2023", "Cor:": "Ex: Prata", "Valor da Diária:": "Ex: 150.00"
        }
        
        self.entradas = {}
        for i, (texto_label, texto_ajuda) in enumerate(campos.items()):
            ttk.Label(frame_formulario, text=texto_label).grid(row=i, column=0, padx=(10, 2), pady=5, sticky="e")
            chave = texto_label.replace(":", "").replace(" ", "_").lower()
            entrada = EntryComTextoDeAjuda(frame_formulario, texto_ajuda=texto_ajuda, width=40)
            entrada.grid(row=i, column=1, padx=(2, 10), pady=5, sticky="ew")
            self.entradas[chave] = entrada

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5)
        
        ttk.Button(frame_botoes, text="➕\u2009Adicionar", style="Emoji.TButton", command=self.adicionar_veiculo).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🔄\u2009Atualizar", style="Emoji.TButton", command=self.atualizar_veiculo).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🗑️\u2009Remover", style="Emoji.TButton", command=self.remover_veiculo).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🧹\u2009Limpar Campos", style="Emoji.TButton", command=self.limpar_campos).pack(side="left", padx=5)

        criar_cabecalho_secao(self, "Lista de Veículos")
        frame_lista = ttk.Frame(self)
        frame_lista.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        colunas = ("placa", "marca", "modelo", "ano", "cor", "valor_diaria", "status")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        for col in colunas:
            self.tree.heading(col, text=obter_cabecalho_exibicao(col))
            self.tree.column(col, width=100, anchor=tk.CENTER)
            
        self.tree.pack(expand=True, fill="both", side="left")
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<ButtonRelease-1>", self.ao_clicar_no_item)

    def popular_lista_veiculos(self):
        self.item_selecionado = None
        for linha in self.tree.get_children():
            self.tree.delete(linha)
        for veiculo in db.listar_veiculos():
            valores_para_exibir = (
                veiculo['placa'].upper(), formatar_texto_capitalizado(veiculo['marca']),
                formatar_texto_capitalizado(veiculo['modelo']), veiculo['ano'],
                formatar_texto_capitalizado(veiculo['cor']), formatar_moeda(veiculo['valor_diaria']),
                veiculo['status']
            )
            self.tree.insert("", "end", values=valores_para_exibir)

    def ao_clicar_no_item(self, event):
        id_item_clicado = self.tree.identify_row(event.y)
        if not id_item_clicado: return
        
        if self.item_selecionado == id_item_clicado:
            self.tree.selection_remove(id_item_clicado)
            self.limpar_campos()
        else:
            self.limpar_campos(limpar_selecao=False)
            self.tree.selection_set(id_item_clicado)
            self.item_selecionado = id_item_clicado
            valores = self.tree.item(id_item_clicado)['values']
            valor_sem_cifrao = str(valores[5]).replace("R$", "").replace(".", "").replace(",", ".").strip()
            
            mapa_entradas = {"placa": valores[0], "marca": valores[1], "modelo": valores[2], 
                             "ano": valores[3], "cor": valores[4], "valor_da_diária": valor_sem_cifrao}
            for chave, valor in mapa_entradas.items():
                self.entradas[chave].delete(0, tk.END)
                self.entradas[chave].insert(0, valor)
                self.entradas[chave].mostrando_texto_ajuda = False
            
            self.entradas["placa"].config(state="disabled")

    def limpar_campos(self, limpar_selecao=True):
        self.entradas["placa"].config(state="normal")
        for entrada in self.entradas.values():
            entrada.delete(0, "end")
            entrada._ao_perder_foco()
        if limpar_selecao and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.item_selecionado = None

    def adicionar_veiculo(self):
        dados = {chave: entrada.get() for chave, entrada in self.entradas.items()}
        if self.entradas['placa'].mostrando_texto_ajuda: dados['placa'] = ''
        sucesso, mensagens = db.adicionar_veiculo(
            dados["placa"], dados["marca"], dados["modelo"], dados["ano"], 
            dados["cor"], dados["valor_da_diária"]
        )
        if sucesso:
            messagebox.showinfo("Sucesso", mensagens[0])
            self.limpar_campos()
            self.popular_lista_veiculos()
        else:
            messagebox.showerror("Erro de Validação", "\n".join(mensagens))

    def atualizar_veiculo(self):
        entrada_placa = self.entradas["placa"]
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para atualizar.")
            return

        entrada_placa.config(state="normal")
        dados = {chave: entrada.get() for chave, entrada in self.entradas.items()}
        entrada_placa.config(state="disabled")

        sucesso, mensagens = db.atualizar_veiculo(
            dados["placa"], dados["marca"], dados["modelo"], dados["ano"], 
            dados["cor"], dados["valor_da_diária"]
        )
        if sucesso:
            messagebox.showinfo("Sucesso", mensagens[0])
            self.limpar_campos()
            self.popular_lista_veiculos()
        else:
            messagebox.showerror("Erro", "\n".join(mensagens))

    def remover_veiculo(self):
        entrada_placa = self.entradas["placa"]
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para remover.")
            return

        entrada_placa.config(state="normal")
        placa = entrada_placa.get()
        entrada_placa.config(state="disabled")

        if messagebox.askyesno("Confirmar Remoção", f"Remover veículo de placa {placa}?"):
            sucesso, mensagens = db.remover_veiculo(placa)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagens[0])
                self.limpar_campos()
                self.popular_lista_veiculos()
            else:
                messagebox.showerror("Erro", "\n".join(mensagens))

# =============================================================================
# ABA DE CLIENTES
# =============================================================================

class AbaClientes(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.item_selecionado = None
        self._criar_widgets()
        self.popular_lista_clientes()

    def _criar_widgets(self):
        criar_cabecalho_secao(self, "Cadastro de Cliente")
        frame_formulario_wrapper = ttk.Frame(self)
        frame_formulario_wrapper.pack(pady=(0, 10))
        frame_formulario = ttk.Frame(frame_formulario_wrapper)
        frame_formulario.pack()

        campos = {
            "CPF:": "123.456.789-00", "Nome:": "Nome Completo do Cliente",
            "Telefone:": "(XX) XXXXX-XXXX", "E-mail:": "email@exemplo.com"
        }
        self.entradas = {}
        for i, (texto_label, texto_ajuda) in enumerate(campos.items()):
            ttk.Label(frame_formulario, text=texto_label).grid(row=i, column=0, padx=(10, 2), pady=5, sticky="e")
            chave = texto_label.replace(":", "").replace("-", "_").lower()
            entrada = EntryComTextoDeAjuda(frame_formulario, texto_ajuda=texto_ajuda, width=40)
            entrada.grid(row=i, column=1, padx=(2, 10), pady=5, sticky="ew")
            self.entradas[chave] = entrada

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5)
        
        ttk.Button(frame_botoes, text="➕\u2009Adicionar", style="Emoji.TButton", command=self.adicionar_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🔄\u2009Atualizar", style="Emoji.TButton", command=self.atualizar_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🗑️\u2009Remover", style="Emoji.TButton", command=self.remover_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🧹\u2009Limpar Campos", style="Emoji.TButton", command=self.limpar_campos).pack(side="left", padx=5)

        criar_cabecalho_secao(self, "Lista de Clientes")
        frame_lista = ttk.Frame(self)
        frame_lista.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        colunas = ("cpf", "nome", "telefone", "email")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        for col in colunas:
            self.tree.heading(col, text=obter_cabecalho_exibicao(col))
            self.tree.column(col, anchor=tk.CENTER)
            
        self.tree.pack(expand=True, fill="both", side="left")
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self.ao_clicar_no_item)
        
    def popular_lista_clientes(self):
        self.item_selecionado = None
        for linha in self.tree.get_children(): self.tree.delete(linha)
        for cliente in db.listar_clientes():
            valores = (
                formatar_cpf(cliente['cpf']),
                formatar_texto_capitalizado(cliente['nome']),
                formatar_telefone(cliente['telefone']),
                cliente['email']
            )
            self.tree.insert("", "end", values=valores)
            
    def ao_clicar_no_item(self, event):
        id_item_clicado = self.tree.identify_row(event.y)
        if not id_item_clicado: return
        
        if self.item_selecionado == id_item_clicado:
            self.tree.selection_remove(id_item_clicado)
            self.limpar_campos()
        else:
            self.limpar_campos(limpar_selecao=False)
            self.tree.selection_set(id_item_clicado)
            self.item_selecionado = id_item_clicado
            valores = self.tree.item(id_item_clicado)['values']
            mapa_entradas = {"cpf": valores[0], "nome": valores[1], "telefone": valores[2], "e_mail": valores[3]}
            for chave, valor in mapa_entradas.items():
                self.entradas[chave].delete(0, tk.END)
                self.entradas[chave].insert(0, valor)
                self.entradas[chave].mostrando_texto_ajuda = False
            self.entradas["cpf"].config(state="disabled")

    def limpar_campos(self, limpar_selecao=True):
        self.entradas["cpf"].config(state="normal")
        for entrada in self.entradas.values():
            entrada.delete(0, "end")
            entrada._ao_perder_foco()
        if limpar_selecao and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.item_selecionado = None

    def adicionar_cliente(self):
        dados = {chave: entrada.get() for chave, entrada in self.entradas.items()}
        sucesso, msgs = db.adicionar_cliente(dados["cpf"], dados["nome"], dados["telefone"], dados["e_mail"])
        if sucesso:
            messagebox.showinfo("Sucesso", msgs[0])
            self.limpar_campos()
            self.popular_lista_clientes()
        else:
            messagebox.showerror("Erro", "\n".join(msgs))

    def atualizar_cliente(self):
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para atualizar.")
            return

        entrada_cpf = self.entradas["cpf"]
        entrada_cpf.config(state="normal")
        dados = {chave: entrada.get() for chave, entrada in self.entradas.items()}
        entrada_cpf.config(state="disabled")

        sucesso, msgs = db.atualizar_cliente(dados["cpf"], dados["nome"], dados["telefone"], dados["e_mail"])
        if sucesso:
            messagebox.showinfo("Sucesso", msgs[0])
            self.limpar_campos()
            self.popular_lista_clientes()
        else:
            messagebox.showerror("Erro", "\n".join(msgs))

    def remover_cliente(self):
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para remover.")
            return

        entrada_cpf = self.entradas["cpf"]
        entrada_cpf.config(state="normal")
        cpf = entrada_cpf.get()
        entrada_cpf.config(state="disabled")

        if messagebox.askyesno("Confirmar Remoção", f"Remover o cliente de CPF {cpf}?"):
            sucesso, msgs = db.remover_cliente(cpf)
            if sucesso:
                messagebox.showinfo("Sucesso", msgs[0])
                self.limpar_campos()
                self.popular_lista_clientes()
            else:
                messagebox.showerror("Erro", "\n".join(msgs))

# =============================================================================
# ABA DE ALUGUÉIS
# =============================================================================

class AbaAlugueis(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.item_selecionado = None
        self._criar_widgets()
        self.popular_alugueis_ativos()
        self.atualizar_sugestoes()

    def _criar_widgets(self):
        criar_cabecalho_secao(self, "Gerenciar Aluguel")
        frame_formulario_wrapper = ttk.Frame(self)
        frame_formulario_wrapper.pack(pady=(0, 10))
        frame_formulario = ttk.Frame(frame_formulario_wrapper)
        frame_formulario.pack()
        
        self.entradas = {}
        ttk.Label(frame_formulario, text="Placa do Carro:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entradas['placa_do_carro'] = ttk.Combobox(frame_formulario, width=38)
        self.entradas['placa_do_carro'].grid(row=0, column=1, padx=(2, 10), pady=5, sticky="ew")
        
        ttk.Label(frame_formulario, text="CPF do Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entradas['cpf_do_cliente'] = ttk.Combobox(frame_formulario, width=38)
        self.entradas['cpf_do_cliente'].grid(row=1, column=1, padx=(2, 10), pady=5, sticky="ew")

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5)
        
        ttk.Button(frame_botoes, text="➕\u2009Realizar Aluguel", style="Emoji.TButton", command=self.realizar_aluguel).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="➡️\u2009Realizar Devolução", style="Emoji.TButton", command=self.realizar_devolucao).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🧹\u2009Limpar Campos", style="Emoji.TButton", command=self.limpar_campos).pack(side="left", padx=5)

        criar_cabecalho_secao(self, "Aluguéis Ativos")
        frame_lista = ttk.Frame(self)
        frame_lista.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        colunas = ("cpf_cliente", "id", "placa_carro", "data_retirada")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        for col in colunas:
            self.tree.heading(col, text=obter_cabecalho_exibicao(col))
            self.tree.column(col, anchor=tk.CENTER)

        self.tree.pack(expand=True, fill="both", side="left")
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<ButtonRelease-1>", self.ao_clicar_no_item)

    def popular_alugueis_ativos(self):
        for linha in self.tree.get_children(): self.tree.delete(linha)
        
        try:
            alugueis = db.listar_alugueis_ativos()
            for aluguel in alugueis:
                valores = (formatar_cpf(aluguel['cpf_cliente']), aluguel['id'], aluguel['placa_carro'].upper(), aluguel['data_retirada'])
                self.tree.insert("", "end", values=valores)
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível buscar os aluguéis:\n{e}")
    
    def ao_clicar_no_item(self, event):
        id_item_clicado = self.tree.identify_row(event.y)
        if not id_item_clicado: return

        if self.item_selecionado == id_item_clicado:
            self.tree.selection_remove(id_item_clicado)
            self.limpar_campos()
        else:
            self.limpar_campos(limpar_selecao=False)
            self.tree.selection_set(id_item_clicado)
            self.item_selecionado = id_item_clicado
            
            valores = self.tree.item(id_item_clicado)['values']
            
            self.entradas['cpf_do_cliente'].set(valores[0])
            self.entradas['placa_do_carro'].set(valores[2])
            
            self.entradas['placa_do_carro'].config(state="disabled")
            self.entradas['cpf_do_cliente'].config(state="disabled")

    def limpar_campos(self, limpar_selecao=True):
        self.entradas['placa_do_carro'].config(state="normal")
        self.entradas['cpf_do_cliente'].config(state="normal")
        
        self.entradas['placa_do_carro'].set('')
        self.entradas['cpf_do_cliente'].set('')

        if limpar_selecao and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.item_selecionado = None

    def realizar_aluguel(self):
        if self.item_selecionado:
            messagebox.showwarning("Ação Inválida", "Limpe a seleção atual antes de registrar um novo aluguel.")
            return

        placa = self.entradas['placa_do_carro'].get()
        cpf = self.entradas['cpf_do_cliente'].get()
        
        sucesso, msgs = db.realizar_aluguel(placa, cpf)
        if sucesso:
            messagebox.showinfo("Sucesso", msgs[0])
            self.limpar_campos()
            self.popular_alugueis_ativos()
            self.atualizar_sugestoes()
        else:
            messagebox.showerror("Erro no Aluguel", "\n".join(msgs))
            
    def realizar_devolucao(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Ação Inválida", "Selecione um aluguel na lista para realizar a devolução.")
            return
        
        placa = self.tree.item(selecao[0])['values'][2]

        if not messagebox.askyesno("Confirmar Devolução", f"Registrar a devolução do veículo de placa {placa}?"):
                return

        sucesso, msgs, _ = db.realizar_devolucao(placa)
        if sucesso:
            messagebox.showinfo("Devolução Realizada", msgs[0])
            self.limpar_campos()
            self.popular_alugueis_ativos()
            self.atualizar_sugestoes()
        else:
            messagebox.showerror("Erro na Devolução", "\n".join(msgs))

    def atualizar_sugestoes(self):
        carros_disponiveis = [carro['placa'].upper() for carro in db.listar_veiculos(status_filtro='Disponível')]
        self.entradas['placa_do_carro']['values'] = carros_disponiveis
        
        cpfs_formatados = [formatar_cpf(c['cpf']) for c in db.listar_clientes()]
        self.entradas['cpf_do_cliente']['values'] = cpfs_formatados

# =============================================================================
# ABA DE MANUTENÇÃO
# =============================================================================

class AbaManutencao(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.item_selecionado_id = None
        self._criar_widgets()
        self.popular_manutencoes_ativas()
        self.atualizar_veiculos_disponiveis()

    def _criar_widgets(self):
        criar_cabecalho_secao(self, "Gerenciar Manutenção de Veículos")
        frame_formulario_wrapper = ttk.Frame(self)
        frame_formulario_wrapper.pack(pady=(0, 10), fill="x")

        frame_formulario = ttk.Frame(frame_formulario_wrapper)
        frame_formulario.pack()
        
        ttk.Label(frame_formulario, text="Veículo Disponível:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_placa_enviar = ttk.Combobox(frame_formulario, width=25)
        self.combo_placa_enviar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_formulario, text="Motivo/Descrição:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="e")
        self.entry_descricao = EntryComTextoDeAjuda(frame_formulario, texto_ajuda="Ex: Troca de óleo", width=30)
        self.entry_descricao.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_formulario, text="Custo Previsto (R$):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_custo = EntryComTextoDeAjuda(frame_formulario, texto_ajuda="Ex: 350.50", width=25)
        self.entry_custo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=10)
        
        ttk.Button(frame_botoes, text="✔️\u2009Enviar para Manutenção", style="Emoji.TButton", command=self.enviar_para_manutencao).pack(side="left", padx=10)
        self.btn_registrar_retorno = ttk.Button(frame_botoes, text="✅\u2009Registrar Retorno", style="Emoji.TButton", command=self.registrar_retorno)
        self.btn_registrar_retorno.pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="🧹\u2009Limpar", style="Emoji.TButton", command=self.limpar_campos).pack(side="left", padx=10)

        criar_cabecalho_secao(self, "Veículos Atualmente em Manutenção")
        frame_lista = ttk.Frame(self)
        frame_lista.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        colunas = ("id", "placa_carro", "descricao", "custo", "data_entrada")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        for col in colunas:
            self.tree.heading(col, text=obter_cabecalho_exibicao(col))
            self.tree.column(col, anchor=tk.CENTER, width=150)
        
        self.tree.column("id", width=60)
        self.tree.column("descricao", width=350)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self.ao_clicar_no_item)
        self.limpar_campos()

    def popular_manutencoes_ativas(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        manutencoes = db.listar_manutencoes(status_filtro='Em Andamento')
        for item in manutencoes:
            valores = (
                item['id'], 
                item['placa_carro'], 
                item['descricao'], 
                formatar_moeda(item['custo']), 
                item['data_entrada']
            )
            self.tree.insert("", "end", values=valores)
        self.limpar_campos()

    def atualizar_veiculos_disponiveis(self):
        veiculos = db.listar_veiculos(status_filtro='Disponível')
        placas = [v['placa'] for v in veiculos]
        self.combo_placa_enviar['values'] = placas
        if placas:
            self.combo_placa_enviar.set('')

    def ao_clicar_no_item(self, event):
        id_item_clicado_str = self.tree.identify_row(event.y)
        if not id_item_clicado_str: 
            self.limpar_campos()
            return
        
        id_item_clicado = self.tree.item(id_item_clicado_str)['values'][0]

        if self.item_selecionado_id == id_item_clicado:
             self.limpar_campos()
        else:
            self.tree.selection_set(id_item_clicado_str)
            self.item_selecionado_id = id_item_clicado
            self.btn_registrar_retorno.config(state="normal")

    def limpar_campos(self):
        self.item_selecionado_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

        self.combo_placa_enviar.set('')
        self.entry_descricao.delete(0, 'end'); self.entry_descricao._ao_perder_foco()
        self.entry_custo.delete(0, 'end'); self.entry_custo._ao_perder_foco()
        
        self.btn_registrar_retorno.config(state="disabled")

    def enviar_para_manutencao(self):
        placa = self.combo_placa_enviar.get()
        descricao = self.entry_descricao.get()
        custo = self.entry_custo.get()
        
        if self.entry_descricao.mostrando_texto_ajuda: descricao = ""
        if self.entry_custo.mostrando_texto_ajuda: custo = ""

        sucesso, msgs = db.enviar_para_manutencao(placa, descricao, custo)
        if sucesso:
            messagebox.showinfo("Sucesso", msgs[0])
            self.popular_manutencoes_ativas()
            self.atualizar_veiculos_disponiveis()
        else:
            messagebox.showerror("Erro", "\n".join(msgs))
            
    def registrar_retorno(self):
        if not self.item_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um veículo na lista para registrar o retorno.")
            return

        if not messagebox.askyesno("Confirmar Retorno", "Deseja confirmar o retorno deste veículo da manutenção?"):
            return
            
        sucesso, msgs = db.registrar_retorno_manutencao(self.item_selecionado_id)
        
        if sucesso:
            messagebox.showinfo("Sucesso", msgs[0])
            self.popular_manutencoes_ativas()
            self.atualizar_veiculos_disponiveis()
        else:
            messagebox.showerror("Erro", "\n".join(msgs))

# =============================================================================
# ABA DE RELATÓRIOS
# =============================================================================

class AbaRelatorios(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.item_selecionado = None
        self._criar_widgets()

    def _criar_widgets(self):
        criar_cabecalho_secao(self, "Filtros de Relatório")
        frame_acoes = ttk.Frame(self)
        frame_acoes.pack(pady=5)
        ttk.Label(frame_acoes, text="CPF do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_cpf_hist = ttk.Combobox(frame_acoes, width=23)
        self.entrada_cpf_hist.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_acoes, text="🔍\u2009Buscar por CPF", style="Emoji.TButton", command=self.buscar_historico_por_cpf).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame_acoes, text="📜\u2009Ver Histórico Geral", style="Emoji.TButton", command=self.ver_historico_geral).grid(row=0, column=3, padx=20, pady=5)
        
        criar_cabecalho_secao(self, "Histórico de Aluguéis")
        frame_lista_hist = ttk.Frame(self)
        frame_lista_hist.pack(expand=True, fill="both", padx=10, pady=(0,5))
        colunas = ("cpf_cliente", "placa_carro", "data_retirada", "data_devolucao", "valor_total", "status")
        self.tree_hist = ttk.Treeview(frame_lista_hist, columns=colunas, show="headings")
        for col in colunas:
            self.tree_hist.heading(col, text=obter_cabecalho_exibicao(col))
            self.tree_hist.column(col, width=130, anchor=tk.CENTER)
        self.tree_hist.pack(expand=True, fill="both", side="left")
        scrollbar_hist = ttk.Scrollbar(frame_lista_hist, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=scrollbar_hist.set)
        scrollbar_hist.pack(side="right", fill="y")
        
        self.tree_hist.bind("<ButtonRelease-1>", self.ao_clicar_no_item)
        
        criar_cabecalho_secao(self, "Calcular Faturamento por Período")
        frame_faturamento_wrapper = ttk.Frame(self)
        frame_faturamento_wrapper.pack(pady=5)
        frame_faturamento = ttk.Frame(frame_faturamento_wrapper)
        frame_faturamento.pack()
        
        ttk.Label(frame_faturamento, text="📅\u2009Data de Início (AAAA-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_data_inicio = EntryComTextoDeAjuda(frame_faturamento, texto_ajuda="Ex: 2025-01-01")
        self.entrada_data_inicio.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_faturamento, text="📅\u2009Data de Fim (AAAA-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_data_fim = EntryComTextoDeAjuda(frame_faturamento, texto_ajuda="Ex: 2025-01-31")
        self.entrada_data_fim.grid(row=1, column=1, padx=5, pady=5)
        
        frame_botao_calcular = ttk.Frame(frame_faturamento)
        frame_botao_calcular.grid(row=0, column=2, rowspan=2, padx=10)
        ttk.Button(frame_botao_calcular, text="💲\u2009Calcular", style="Emoji.TButton", command=self.calcular_faturamento).pack()

        self.label_faturamento = ttk.Label(frame_faturamento, text="Faturamento Total: R$ 0,00", font=("Arial", 12, "bold"))
        self.label_faturamento.grid(row=0, column=3, rowspan=2, padx=20)

    def atualizar_sugestoes_cpf(self):
        clientes = db.listar_clientes()
        cpfs_formatados = [formatar_cpf(c['cpf']) for c in clientes]
        self.entrada_cpf_hist['values'] = cpfs_formatados
        if cpfs_formatados:
            self.entrada_cpf_hist.set('')

    def ao_clicar_no_item(self, event):
        id_item_clicado = self.tree_hist.identify_row(event.y)
        if not id_item_clicado: return
        
        if self.item_selecionado == id_item_clicado:
            self.tree_hist.selection_remove(id_item_clicado)
            self.item_selecionado = None
        else:
            self.tree_hist.selection_set(id_item_clicado)
            self.item_selecionado = id_item_clicado
            
    def _popular_historico(self, historico_completo):
        self.item_selecionado = None
        for linha in self.tree_hist.get_children(): self.tree_hist.delete(linha)
        
        if not historico_completo:
            messagebox.showinfo("Histórico", "Nenhum registro encontrado.")
            return
            
        for item in historico_completo:
            data_devolucao_val = item.get('data_devolucao')
            data_devolucao_display = data_devolucao_val if data_devolucao_val else "Pendente"
            valor = formatar_moeda(item.get('valor_total')) if data_devolucao_val else "N/A"
            valores_tupla = (
                formatar_cpf(item.get('cpf_cliente', 'N/A')),
                item.get('placa_carro', 'N/A').upper(),
                item.get('data_retirada', 'N/A'),
                data_devolucao_display, valor,
                item.get('status', 'N/A')
            )
            self.tree_hist.insert("", "end", values=valores_tupla)
            
    def buscar_historico_por_cpf(self):
        cpf = self.entrada_cpf_hist.get()
        if not cpf:
            messagebox.showwarning("Aviso", "Por favor, insira um CPF.")
            return
        historico = db.buscar_historico(filtro_cpf=cpf)
        self._popular_historico(historico)
            
    def ver_historico_geral(self):
        historico = db.buscar_historico()
        self._popular_historico(historico)

    def calcular_faturamento(self):
        data_inicio = self.entrada_data_inicio.get()
        data_fim = self.entrada_data_fim.get()

        if self.entrada_data_inicio.mostrando_texto_ajuda or self.entrada_data_fim.mostrando_texto_ajuda:
            messagebox.showwarning("Aviso", "As datas de início e fim são obrigatórias.")
            return

        sucesso, resultado = db.calcular_faturamento_periodo(data_inicio, data_fim)
        if sucesso:
            self.label_faturamento.config(text=f"Faturamento Total: {formatar_moeda(resultado)}")
        else:
            messagebox.showerror("Erro de Data", resultado[0])

if __name__ == '__main__':
    app = LocadoraApp()
    app.mainloop()
