# database.py (Atualizado)

import sqlite3
import re
from datetime import datetime
import math

# =============================================================================
# CONFIGURAÇÃO E CONEXÃO COM O BANCO DE DADOS
# =============================================================================

NOME_BANCO_DADOS = 'locadora.db'

def conectar_bd():
    """Conecta ao banco de dados SQLite e retorna a conexão e o cursor."""
    conn = sqlite3.connect(NOME_BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def criar_tabelas():
    """Cria as tabelas do banco de dados se elas não existirem."""
    conn, cursor = conectar_bd()
    try:
        # Tabela de Veículos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                placa TEXT PRIMARY KEY,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                ano INTEGER NOT NULL,
                cor TEXT NOT NULL,
                valor_diaria REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Disponível'
            );
        """)
        
        # Tabela de Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                cpf TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT UNIQUE
            );
        """)
        
        # Tabela de Aluguéis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alugueis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa_carro TEXT NOT NULL,
                cpf_cliente TEXT NOT NULL,
                data_retirada TEXT NOT NULL,
                data_devolucao TEXT,
                valor_total REAL,
                status TEXT NOT NULL,
                FOREIGN KEY (placa_carro) REFERENCES veiculos (placa) ON DELETE RESTRICT,
                FOREIGN KEY (cpf_cliente) REFERENCES clientes (cpf) ON DELETE RESTRICT
            );
        """)

        # Tabela de Manutenções (NOVA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa_carro TEXT NOT NULL,
                data_entrada TEXT NOT NULL,
                data_saida TEXT,
                descricao TEXT NOT NULL,
                custo REAL,
                status TEXT NOT NULL,
                FOREIGN KEY (placa_carro) REFERENCES veiculos (placa) ON DELETE RESTRICT
            );
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

# =============================================================================
# FUNÇÕES DE VALIDAÇÃO (Sem alterações)
# =============================================================================

def validar_placa(placa):
    """Valida placas no formato antigo (ABC-1234) e Mercosul (ABC1D23)."""
    if not isinstance(placa, str) or not placa.strip():
        return "O campo 'Placa' é obrigatório."
    placa = placa.upper().strip()
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    padrao_antigo = re.compile(r'^[A-Z]{3}-\d{4}$')
    if padrao_mercosul.match(placa) or padrao_antigo.match(placa.replace("-", "")):
        return None
    return "Formato de placa inválido. Use 'ABC-1234' ou 'ABC1D23'."

def validar_ano(ano):
    """Valida se o ano é um número e está num intervalo razoável."""
    if not ano: return "O campo 'Ano' é obrigatório."
    try:
        ano_int = int(ano)
        ano_atual = datetime.now().year
        if not (1950 <= ano_int <= ano_atual + 1):
            return f"Ano inválido. Deve ser entre 1950 e {ano_atual + 1}."
        return None
    except (ValueError, TypeError):
        return "O ano deve ser um número inteiro válido."

def validar_valor(valor):
    """Valida se o valor é um número positivo."""
    if not valor: return "O campo 'Valor' é obrigatório."
    try:
        valor_float = float(str(valor).replace(",", "."))
        if valor_float < 0:
            return "O valor não pode ser negativo."
        return None
    except (ValueError, TypeError):
        return "O valor deve ser um número válido."

def validar_cpf(cpf):
    """Valida um CPF brasileiro."""
    if not cpf: return "O campo 'CPF' é obrigatório."
    cpf_numerico = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf_numerico) != 11 or len(set(cpf_numerico)) == 1:
        return "CPF inválido. Verifique o número digitado."
    
    soma = sum(int(cpf_numerico[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10) % 11
    if d1 == 10: d1 = 0
    if d1 != int(cpf_numerico[9]):
        return "CPF inválido. Verifique o número digitado."

    soma = sum(int(cpf_numerico[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10) % 11
    if d2 == 10: d2 = 0
    if d2 != int(cpf_numerico[10]):
        return "CPF inválido. Verifique o número digitado."

    return None

# =============================================================================
# OPERAÇÕES CRUD - VEÍCULOS (Sem alterações)
# =============================================================================

def adicionar_veiculo(placa, marca, modelo, ano, cor, valor_diaria):
    erros = list(filter(None, [
        validar_placa(placa),
        "O campo 'Marca' é obrigatório." if not marca.strip() else None,
        "O campo 'Modelo' é obrigatório." if not modelo.strip() else None,
        validar_ano(ano),
        "O campo 'Cor' é obrigatório." if not cor.strip() else None,
        validar_valor(valor_diaria)
    ]))
    if erros:
        return (False, erros)

    conn, cursor = conectar_bd()
    try:
        cursor.execute(
            "INSERT INTO veiculos (placa, marca, modelo, ano, cor, valor_diaria) VALUES (?, ?, ?, ?, ?, ?)",
            (placa.upper().strip(), marca.strip(), modelo.strip(), int(ano), cor.strip(), float(str(valor_diaria).replace(",", ".")))
        )
        conn.commit()
        return (True, ["Veículo adicionado com sucesso."])
    except sqlite3.IntegrityError:
        return (False, [f"A placa '{placa.upper().strip()}' já está cadastrada."])
    finally:
        conn.close()

def atualizar_veiculo(placa, marca, modelo, ano, cor, valor_diaria):
    erros = list(filter(None, [
        "O campo 'Marca' é obrigatório." if not marca.strip() else None,
        "O campo 'Modelo' é obrigatório." if not modelo.strip() else None,
        validar_ano(ano),
        "O campo 'Cor' é obrigatório." if not cor.strip() else None,
        validar_valor(valor_diaria)
    ]))
    if erros:
        return (False, erros)

    conn, cursor = conectar_bd()
    try:
        cursor.execute(
            "UPDATE veiculos SET marca=?, modelo=?, ano=?, cor=?, valor_diaria=? WHERE placa=?",
            (marca.strip(), modelo.strip(), int(ano), cor.strip(), float(str(valor_diaria).replace(",", ".")), placa.upper().strip())
        )
        conn.commit()
        return (True, ["Veículo atualizado com sucesso."])
    except Exception as e:
        return (False, [f"Erro ao atualizar veículo: {e}"])
    finally:
        conn.close()

def remover_veiculo(placa):
    conn, cursor = conectar_bd()
    try:
        cursor.execute("DELETE FROM veiculos WHERE placa = ?", (placa.upper().strip(),))
        if cursor.rowcount == 0:
            return (False, [f"Nenhum veículo encontrado com a placa '{placa.upper().strip()}'."])
        conn.commit()
        return (True, ["Veículo removido com sucesso."])
    except sqlite3.IntegrityError:
        return (False, ["Não é possível remover o veículo, pois ele possui um histórico de aluguéis ou manutenções."])
    finally:
        conn.close()

def listar_veiculos(status_filtro=None):
    conn, cursor = conectar_bd()
    query = "SELECT * FROM veiculos"
    params = []
    if status_filtro:
        query += " WHERE status = ?"
        params.append(status_filtro)
    cursor.execute(query, params)
    veiculos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return veiculos

# =============================================================================
# OPERAÇÕES CRUD - CLIENTES (Sem alterações)
# =============================================================================

def adicionar_cliente(cpf, nome, telefone, email):
    erros = list(filter(None, [
        validar_cpf(cpf),
        "O campo 'Nome' é obrigatório." if not nome.strip() else None
    ]))
    if erros:
        return (False, erros)
    
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    conn, cursor = conectar_bd()
    try:
        cursor.execute(
            "INSERT INTO clientes (cpf, nome, telefone, email) VALUES (?, ?, ?, ?)",
            (cpf_limpo, nome.strip(), telefone.strip(), email.strip().lower())
        )
        conn.commit()
        return (True, ["Cliente adicionado com sucesso."])
    except sqlite3.IntegrityError as e:
        if "clientes.cpf" in str(e):
            return (False, [f"O CPF '{cpf_limpo}' já está cadastrado."])
        if "clientes.email" in str(e):
            return (False, [f"O e-mail '{email.strip().lower()}' já está em uso."])
        return (False, [f"Erro no banco de dados: {e}"])
    finally:
        conn.close()

def atualizar_cliente(cpf, nome, telefone, email):
    erros = list(filter(None, [
        validar_cpf(cpf),
        "O campo 'Nome' é obrigatório." if not nome.strip() else None
    ]))
    if erros:
        return (False, erros)
        
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    conn, cursor = conectar_bd()
    try:
        cursor.execute(
            "UPDATE clientes SET nome=?, telefone=?, email=? WHERE cpf=?",
            (nome.strip(), telefone.strip(), email.strip().lower(), cpf_limpo)
        )
        conn.commit()
        return (True, ["Cliente atualizado com sucesso."])
    except sqlite3.IntegrityError:
        return (False, [f"O e-mail '{email.strip().lower()}' já está em uso por outro cliente."])
    finally:
        conn.close()

def remover_cliente(cpf):
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    conn, cursor = conectar_bd()
    try:
        cursor.execute("DELETE FROM clientes WHERE cpf = ?", (cpf_limpo,))
        if cursor.rowcount == 0:
            return (False, [f"Nenhum cliente encontrado com o CPF '{cpf_limpo}'."])
        conn.commit()
        return (True, ["Cliente removido com sucesso."])
    except sqlite3.IntegrityError:
        return (False, ["Não é possível remover o cliente, pois ele possui um histórico de aluguéis."])
    finally:
        conn.close()

def listar_clientes():
    conn, cursor = conectar_bd()
    cursor.execute("SELECT * FROM clientes")
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes

# =============================================================================
# OPERAÇÕES DE ALUGUEL (Sem alterações)
# =============================================================================

def realizar_aluguel(placa_carro, cpf_cliente):
    if not placa_carro or not cpf_cliente:
        return (False, ["Placa do carro e CPF do cliente são obrigatórios."])

    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT status FROM veiculos WHERE placa = ?", (placa_carro.upper().strip(),))
        carro = cursor.fetchone()
        if not carro:
            return (False, ["Veículo não encontrado."])
        if carro['status'] != 'Disponível':
            return (False, [f"Veículo não está disponível (Status: {carro['status']})."])

        cpf_limpo = ''.join(filter(str.isdigit, str(cpf_cliente)))
        cursor.execute("SELECT nome FROM clientes WHERE cpf = ?", (cpf_limpo,))
        if not cursor.fetchone():
            return (False, ["Cliente não encontrado."])

        data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO alugueis (placa_carro, cpf_cliente, data_retirada, status) VALUES (?, ?, ?, ?)",
            (placa_carro.upper().strip(), cpf_limpo, data_hoje, 'Ativo')
        )
        cursor.execute("UPDATE veiculos SET status = 'Alugado' WHERE placa = ?", (placa_carro.upper().strip(),))
        conn.commit()
        return (True, ["Aluguel registrado com sucesso."])
    except Exception as e:
        return (False, [f"Erro ao realizar aluguel: {e}"])
    finally:
        conn.close()

def realizar_devolucao(placa_carro):
    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT * FROM alugueis WHERE placa_carro = ? AND status = 'Ativo'", (placa_carro.upper().strip(),))
        aluguel = cursor.fetchone()
        if not aluguel:
            return (False, ["Nenhum aluguel ativo encontrado para este veículo."], None)

        cursor.execute("SELECT valor_diaria FROM veiculos WHERE placa = ?", (placa_carro.upper().strip(),))
        carro = cursor.fetchone()
        valor_diaria = carro['valor_diaria']

        data_retirada = datetime.strptime(aluguel["data_retirada"], "%Y-%m-%d %H:%M:%S")
        data_devolucao = datetime.now()
        duracao = data_devolucao - data_retirada
        dias_alugado = math.ceil(duracao.total_seconds() / 86400)
        dias_alugado = max(1, dias_alugado) 
        valor_total = dias_alugado * valor_diaria

        cursor.execute(
            "UPDATE alugueis SET data_devolucao = ?, valor_total = ?, status = 'Finalizado' WHERE id = ?",
            (data_devolucao.strftime('%Y-%m-%d %H:%M:%S'), valor_total, aluguel['id'])
        )
        cursor.execute("UPDATE veiculos SET status = 'Disponível' WHERE placa = ?", (placa_carro.upper().strip(),))
        conn.commit()
        
        msg = f"Devolução realizada. Total: R$ {valor_total:.2f} ({dias_alugado} dia(s))."
        return (True, [msg], valor_total)
    except Exception as e:
        return (False, [f"Erro ao realizar devolução: {e}"], None)
    finally:
        conn.close()

# =============================================================================
# OPERAÇÕES DE MANUTENÇÃO (NOVAS)
# =============================================================================

def enviar_para_manutencao(placa, descricao):
    """Envia um veículo para manutenção e atualiza seu status."""
    if not placa or not descricao.strip():
        return (False, ["Placa e descrição são obrigatórios."])

    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT status FROM veiculos WHERE placa = ?", (placa.upper(),))
        veiculo = cursor.fetchone()
        if not veiculo:
            return (False, ["Veículo não encontrado."])
        if veiculo['status'] != 'Disponível':
            return (False, [f"Apenas veículos 'Disponíveis' podem ser enviados para manutenção. Status atual: {veiculo['status']}."])

        data_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO manutencoes (placa_carro, data_entrada, descricao, status) VALUES (?, ?, ?, ?)",
            (placa.upper(), data_entrada, descricao.strip(), 'Em Andamento')
        )
        cursor.execute("UPDATE veiculos SET status = 'Em Manutenção' WHERE placa = ?", (placa.upper(),))
        conn.commit()
        return (True, ["Veículo enviado para manutenção com sucesso."])
    except Exception as e:
        conn.rollback()
        return (False, [f"Erro ao enviar para manutenção: {e}"])
    finally:
        conn.close()

def registrar_retorno_manutencao(manutencao_id, custo):
    """Registra o retorno de um veículo da manutenção."""
    erro_custo = validar_valor(custo)
    if erro_custo:
        return (False, [erro_custo])

    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT placa_carro FROM manutencoes WHERE id = ?", (manutencao_id,))
        manutencao = cursor.fetchone()
        if not manutencao:
            return (False, ["Registro de manutenção não encontrado."])

        placa = manutencao['placa_carro']
        data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        custo_float = float(str(custo).replace(",", "."))
        
        cursor.execute(
            "UPDATE manutencoes SET data_saida = ?, custo = ?, status = 'Concluída' WHERE id = ?",
            (data_saida, custo_float, manutencao_id)
        )
        cursor.execute("UPDATE veiculos SET status = 'Disponível' WHERE placa = ?", (placa,))
        conn.commit()
        return (True, ["Retorno da manutenção registrado com sucesso."])
    except Exception as e:
        conn.rollback()
        return (False, [f"Erro ao registrar retorno: {e}"])
    finally:
        conn.close()

def listar_manutencoes(status_filtro=None):
    """Lista as manutenções, com filtro opcional por status."""
    conn, cursor = conectar_bd()
    query = "SELECT * FROM manutencoes"
    params = []
    if status_filtro:
        query += " WHERE status = ?"
        params.append(status_filtro)
    query += " ORDER BY data_entrada DESC"
    cursor.execute(query, params)
    manutencoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return manutencoes

# =============================================================================
# CONSULTAS E RELATÓRIOS (Sem alterações)
# =============================================================================

def listar_alugueis_ativos():
    conn, cursor = conectar_bd()
    cursor.execute("SELECT * FROM alugueis WHERE status = 'Ativo' ORDER BY data_retirada DESC")
    alugueis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alugueis

def buscar_historico(filtro_cpf=None):
    conn, cursor = conectar_bd()
    query = "SELECT * FROM alugueis"
    params = []
    if filtro_cpf:
        cpf_numerico = ''.join(filter(str.isdigit, str(filtro_cpf)))
        query += " WHERE cpf_cliente = ?"
        params.append(cpf_numerico)
    
    query += " ORDER BY data_retirada DESC"
    cursor.execute(query, params)
    historico = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return historico

def calcular_faturamento_periodo(data_inicio, data_fim):
    try:
        datetime.strptime(data_inicio, '%Y-%m-%d')
        datetime.strptime(data_fim, '%Y-%m-%d')
    except (ValueError, TypeError):
        return (False, ["Formato de data inválido. Use 'AAAA-MM-DD'."])

    conn, cursor = conectar_bd()
    try:
        cursor.execute("""
            SELECT SUM(valor_total) AS faturamento
            FROM alugueis
            WHERE status = 'Finalizado' AND date(data_devolucao) BETWEEN ? AND ?
        """, (data_inicio, data_fim))
        
        resultado = cursor.fetchone()
        faturamento = resultado['faturamento'] if resultado['faturamento'] is not None else 0
        return (True, faturamento)
    except Exception as e:
        return (False, [f"Erro ao calcular faturamento: {e}"])
    finally:
        conn.close()