import subprocess
import os

def list_workspaces(ip, login, senha, os_type):
    """
    Returns a tuple: (success_boolean, list_of_shares_or_empty, error_message_or_empty)
    """
    shares = []
    try:
        if os_type == "Darwin":
            cmd = ["smbutil", "view", f"//{login}:{senha}@{ip}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, [], "Falha na conexão (Verifique as credenciais ou o endereço)."
            
            lines = result.stdout.splitlines()
            start_parsing = False
            for line in lines:
                if line.startswith("---"):
                    start_parsing = True
                    continue
                if start_parsing and line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and (parts[-1] == "Disk" or "Disk" in parts):
                        idx = parts.index("Disk") if "Disk" in parts else -1
                        if idx > 0:
                            share_name = " ".join(parts[:idx])
                            shares.append(share_name)
                            
        elif os_type == "Windows":
            # Autenticar primeiro
            auth_cmd = ["net", "use", f"\\\\{ip}\\IPC$", senha, f"/user:{login}"]
            auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
            
            if auth_result.returncode != 0:
                return False, [], "Falha na conexão (Verifique as credenciais ou o endereço)."
                
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
        else:
            return False, [], f"OS não suportado: {os_type}"

        # Filtrar compartilhamentos administrativos comuns
        filtered_shares = [s for s in shares if not s.endswith("$") and s.upper() != "IPC$"]
        return True, filtered_shares, ""

    except Exception as e:
        return False, [], f"Erro interno: {str(e)}"


def mount_workspaces(ip, login, senha, shares, os_type):
    """
    Returns a tuple: (success_count, string_with_errors)
    """
    success_count = 0
    errors = []
    
    try:
        for share in shares:
            if os_type == "Darwin":
                cmd = ["osascript", "-e", f'mount volume "smb://{login}:{senha}@{ip}/{share}"']
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    success_count += 1
                else:
                    errors.append(f"{share}: {res.stderr.strip()}")
                    
            elif os_type == "Windows":
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
                
                # Verifica se a letra já está em uso localmente
                if os.path.exists(letter + "\\"):
                    errors.append(f"{share}: A letra da unidade {letter} já está em uso no seu computador.")
                    continue
                
                cmd = ["net", "use", letter, rf"\\{ip}\{share}", senha, f"/user:{login}"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                
                if res.returncode == 0:
                    success_count += 1
                else:
                    errors.append(f"{share}: {res.stderr.strip() or res.stdout.strip()}")
        
        error_str = "\n".join(errors) if errors else ""
        return success_count, error_str

    except Exception as e:
        return 0, f"Erro crítico ao mapear: {str(e)}"
