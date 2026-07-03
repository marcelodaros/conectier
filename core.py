import subprocess
import os

def list_workspaces(ip, login, senha):
    """
    Returns a tuple: (success_boolean, list_of_shares_or_empty, error_message_or_empty)
    """
    shares = []
    try:
        auth_cmd = ["net", "use", f"\\\\{ip}\\IPC$", senha, f"/user:{login}"]
        auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
        
        if auth_result.returncode != 0:
            error_msg = auth_result.stderr.strip() or auth_result.stdout.strip()
            
            # Se for erro 1219 (múltiplas conexões com usuários diferentes)
            if "1219" in error_msg:
                # Tenta desconectar a sessão fantasma anterior e tentar de novo
                subprocess.run(["net", "use", f"\\\\{ip}\\IPC$", "/delete", "/y"], capture_output=True)
                subprocess.run(["net", "use", f"\\\\{ip}", "/delete", "/y"], capture_output=True)
                
                auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
                
                if auth_result.returncode != 0:
                    return False, [], (
                        "Erro 1219 (Conexão Bloqueada pelo Windows).\n"
                        "Você já possui pastas deste servidor abertas ou mapeadas com outro usuário.\n"
                        "Solução: Feche as pastas, desconecte as unidades de rede atuais deste servidor "
                        "no 'Meu Computador' e tente novamente."
                    )
            else:
                return False, [], f"Falha na conexão (Autenticação Windows):\n{error_msg}"
            
        # Listar shares
        view_cmd = ["net", "view", f"\\\\{ip}"]
        view_result = subprocess.run(view_cmd, capture_output=True, text=True)
        
        lines = view_result.stdout.splitlines()
        start_parsing = False
        for line in lines:
            if line.startswith("---"):
                start_parsing = True
                continue
            if start_parsing and line.strip() and not line.startswith("O comando"):
                if " Disk " in line or " Disco " in line:
                    share_name = line[:line.find(" Disk")].strip()
                    if not share_name:
                        share_name = line[:line.find(" Disco")].strip()
                    shares.append(share_name)

        # Filtrar compartilhamentos administrativos comuns
        filtered_shares = [s for s in shares if not s.endswith("$") and s.upper() != "IPC$"]
        return True, filtered_shares, ""

    except Exception as e:
        return False, [], f"Erro interno: {str(e)}"


def _get_network_drive_letters():
    """
    Returns a dict mapping drive letters (e.g. 'Z:') to their remote UNC paths
    for all currently mapped network drives (including disconnected persistent ones).
    Uses 'net use' output.
    """
    net_drives = {}
    try:
        res = subprocess.run(["net", "use"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            # Lines look like: "OK  Z:  \\server\share  Microsoft Windows Network"
            # or "Unavailable  Z:  \\server\share  ..."
            parts = line.split()
            if len(parts) >= 3:
                # Find a token that looks like a drive letter (e.g. 'Z:')
                for i, token in enumerate(parts):
                    if len(token) == 2 and token[0].isalpha() and token[1] == ':':
                        letter = token.upper()
                        # The UNC path usually follows the letter
                        if i + 1 < len(parts) and parts[i + 1].startswith("\\\\"):
                            net_drives[letter] = parts[i + 1]
                        else:
                            net_drives[letter] = ""
                        break
    except Exception:
        pass
    return net_drives


def mount_workspaces(ip, login, senha, shares):
    """
    Returns a tuple: (success_count, string_with_errors)
    """
    success_count = 0
    errors = []
    
    try:
        # Formata o login para incluir o IP se não houver domínio, essencial para o Windows salvar corretamente
        user_for_cmdkey = login
        if "\\" not in login and "@" not in login:
            user_for_cmdkey = f"{ip}\\{login}"

        # Salva as credenciais no Windows Credential Manager.
        # O target deve ser o IP puro (sem prefixo \\): cmdkey rejeita "\\ip"
        # com "The parameter is incorrect" em algumas builds do Windows.
        # O Windows resolve a credencial pelo nome do servidor ao reconectar
        # as unidades persistentes após reiniciar.
        cmdkey_res = subprocess.run(
            ["cmdkey", f"/add:{ip}", f"/user:{user_for_cmdkey}", f"/pass:{senha}"],
            capture_output=True, text=True
        )
        if cmdkey_res.returncode != 0:
            err = cmdkey_res.stderr.strip() or cmdkey_res.stdout.strip() or f"codigo {cmdkey_res.returncode}"
            errors.append(
                f"Falha ao salvar credenciais no Windows Credential Manager: {err}. "
                "A reconexão após reinicialização pode não funcionar."
            )

        # Obtém as unidades de rede já mapeadas (incluindo as desconectadas/persistentes)
        network_drives = _get_network_drive_letters()

        for share in shares:
            txt_path = rf"\\{ip}\{share}\win_letter.txt"
            letter = None
            
            # Exige o arquivo win_letter.txt
            if not os.path.exists(txt_path):
                errors.append(f"{share}: Arquivo win_letter.txt não encontrado na raiz da pasta.")
                continue
                
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content.isalpha() and len(content) == 1:
                        letter = f"{content.upper()}:"
                    elif content.endswith(":") and len(content) == 2 and content[0].isalpha():
                        letter = content.upper()
            except Exception as e:
                errors.append(f"{share}: Erro ao ler win_letter.txt: {e}")
                continue
                
            if not letter:
                errors.append(f"{share}: Arquivo win_letter.txt não contém uma letra de unidade válida (ex: Z).")
                continue
            
            # Verifica se a letra está em uso:
            # - Se for uma unidade de REDE apontando para este mesmo servidor, remove e remapeia.
            # - Se for uma unidade de REDE de outro servidor, reporta conflito.
            # - Se for uma unidade LOCAL (não está na lista de rede mas existe no sistema), aborta.
            if letter in network_drives:
                existing_unc = network_drives[letter]
                if existing_unc.lower().startswith(f"\\\\{ip.lower()}"):
                    # Mesma origem: remove o mapeamento antigo para remontar limpo
                    subprocess.run(["net", "use", letter, "/delete", "/y"], capture_output=True)
                else:
                    errors.append(
                        f"{share}: A letra {letter} já está em uso por outra unidade de rede ({existing_unc})."
                    )
                    continue
            elif os.path.exists(letter + "\\"):
                # A letra existe no sistema mas não é uma unidade de rede: é local → não mapear
                errors.append(f"{share}: A letra da unidade {letter} já está em uso por uma unidade local.")
                continue
            
            # Mapeia a unidade. As credenciais serão buscadas no Credential Manager no reboot.
            cmd = ["net", "use", letter, rf"\\{ip}\{share}", "/persistent:yes"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0:
                success_count += 1
            else:
                errors.append(f"{share}: {res.stderr.strip() or res.stdout.strip()}")
        
        error_str = "\n".join(errors) if errors else ""
        return success_count, error_str

    except Exception as e:
        return 0, f"Erro crítico ao mapear: {str(e)}"

def disconnect_all():
    """
    Desconecta todas as unidades de rede mapeadas.
    Retorna uma tupla: (sucesso_boolean, mensagem)
    """
    try:
        # O comando do Windows abaixo força a exclusão de todos os mapeamentos de rede ativos
        cmd = ["net", "use", "*", "/delete", "/y"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return True, "Todas as unidades e conexões de rede foram desconectadas no Windows."
        else:
            error_msg = res.stderr.strip() or res.stdout.strip()
            # Se não houver conexões, o Windows diz que a lista está vazia
            if "Não há entradas na lista" in error_msg or "There are no entries in the list" in error_msg:
                return True, "Não havia nenhuma conexão de rede ativa para desconectar."
            return False, f"Erro ao desconectar (Windows): {error_msg}"
            
    except Exception as e:
        return False, f"Erro crítico ao tentar desconectar: {str(e)}"
