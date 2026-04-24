import sys
import platform
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget,
                             QAbstractItemView, QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFontDatabase, QFont

# qt_material deve ser importado após os componentes do PyQt
from qt_material import apply_stylesheet

# Importa a lógica de negócio separada da interface
import core

class WorkerListWorkspaces(QThread):
    finished = pyqtSignal(bool, list, str)  # success, shares, error_msg

    def __init__(self, ip, login, senha, os_type):
        super().__init__()
        self.ip = ip
        self.login = login
        self.senha = senha
        self.os_type = os_type

    def run(self):
        success, shares, error_msg = core.list_workspaces(
            self.ip, self.login, self.senha, self.os_type
        )
        self.finished.emit(success, shares, error_msg)


class WorkerMountWorkspaces(QThread):
    finished = pyqtSignal(int, str)  # success_count, error_msgs

    def __init__(self, ip, login, senha, shares, os_type):
        super().__init__()
        self.ip = ip
        self.login = login
        self.senha = senha
        self.shares = shares
        self.os_type = os_type

    def run(self):
        success_count, error_str = core.mount_workspaces(
            self.ip, self.login, self.senha, self.shares, self.os_type
        )
        self.finished.emit(success_count, error_str)


class WorkerDisconnectAll(QThread):
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, os_type):
        super().__init__()
        self.os_type = os_type

    def run(self):
        success, msg = core.disconnect_all(self.os_type)
        self.finished.emit(success, msg)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.os_type = platform.system()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Conectier")
        self.resize(450, 600)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Conectier\nConecte-se aos servidores")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Container for inputs
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        # IP
        lbl_ip = QLabel("Endereço IP ou Hostname do Servidor")
        lbl_ip.setStyleSheet("color: #b0b0b0;")
        input_layout.addWidget(lbl_ip)
        self.entry_ip = QLineEdit()
        self.entry_ip.setPlaceholderText("Ex: 192.168.1.100")
        self.entry_ip.setStyleSheet("QLineEdit { placeholder-text-color: #a0a0a0; }")
        input_layout.addWidget(self.entry_ip)

        # Login
        lbl_login = QLabel("Usuário de Rede")
        lbl_login.setStyleSheet("color: #b0b0b0;")
        input_layout.addWidget(lbl_login)
        self.entry_login = QLineEdit()
        self.entry_login.setPlaceholderText("Seu nome de usuário")
        self.entry_login.setStyleSheet("QLineEdit { placeholder-text-color: #a0a0a0; }")
        input_layout.addWidget(self.entry_login)

        # Password
        lbl_senha = QLabel("Senha")
        lbl_senha.setStyleSheet("color: #b0b0b0;")
        input_layout.addWidget(lbl_senha)
        self.entry_senha = QLineEdit()
        self.entry_senha.setEchoMode(QLineEdit.Password)
        self.entry_senha.setPlaceholderText("Sua senha")
        self.entry_senha.setStyleSheet("QLineEdit { placeholder-text-color: #a0a0a0; }")
        input_layout.addWidget(self.entry_senha)

        main_layout.addWidget(input_frame)

        # Connect Button
        self.btn_conectar = QPushButton("BUSCAR COMPARTILHAMENTOS")
        self.btn_conectar.setCursor(Qt.PointingHandCursor)
        self.btn_conectar.clicked.connect(self.on_connect_click)
        # Add a custom property so qt-material renders it as a primary colored button
        self.btn_conectar.setProperty('class', 'success')
        main_layout.addWidget(self.btn_conectar)

        # Listbox for shares
        lbl_shares = QLabel("Compartilhamentos Disponíveis (Selecione os que deseja mapear):")
        lbl_shares.setStyleSheet("color: #b0b0b0;")
        main_layout.addWidget(lbl_shares)
        self.listbox_shares = QListWidget()
        self.listbox_shares.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listbox_shares.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.listbox_shares)

        # Mount Button
        self.btn_mapear = QPushButton("MAPEAR SELECIONADOS")
        self.btn_mapear.setCursor(Qt.PointingHandCursor)
        self.btn_mapear.setProperty('class', 'primary')
        self.btn_mapear.clicked.connect(self.on_map_click)
        main_layout.addWidget(self.btn_mapear)

        # Disconnect All Button
        self.btn_desconectar = QPushButton("DESCONECTAR TUDO")
        self.btn_desconectar.setCursor(Qt.PointingHandCursor)
        self.btn_desconectar.setProperty('class', 'danger')
        self.btn_desconectar.clicked.connect(self.on_disconnect_click)
        main_layout.addWidget(self.btn_desconectar)

        # Status Label
        self.lbl_status = QLabel("Pronto para conectar.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("font-weight: bold; padding-top: 10px;")
        main_layout.addWidget(self.lbl_status)

        self.setLayout(main_layout)

    def set_status(self, msg, color_class="primary"):
        color_map = {
            "primary": "#ffffff", # Default light text in dark theme
            "success": "#17a2b8", # Teal/Blue
            "warning": "#e6a23c",
            "danger": "#f56c6c"
        }
        color = color_map.get(color_class, color_map["primary"])
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; padding-top: 10px;")

    def on_connect_click(self):
        ip = self.entry_ip.text().strip()
        login = self.entry_login.text().strip()
        senha = self.entry_senha.text().strip()

        if not ip or not login or not senha:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos (IP, Usuário e Senha).")
            return

        self.set_status("Testando conexão e buscando pastas...", "warning")
        self.btn_conectar.setEnabled(False)
        self.listbox_shares.clear()

        # Inicia a thread separada para não travar a UI
        self.worker_list = WorkerListWorkspaces(ip, login, senha, self.os_type)
        self.worker_list.finished.connect(self.on_list_finished)
        self.worker_list.start()

    def on_list_finished(self, success, shares, error_msg):
        self.btn_conectar.setEnabled(True)
        
        if not success:
            self.set_status(error_msg, "danger")
            return

        if not shares:
            self.set_status("Conectado, mas nenhum disco/compartilhamento encontrado.", "warning")
            return

        for s in shares:
            self.listbox_shares.addItem(s)
            
        self.set_status(f"{len(shares)} pastas encontradas. Selecione para mapear.", "success")

    def on_map_click(self):
        selected_items = self.listbox_shares.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um compartilhamento na lista.")
            return

        ip = self.entry_ip.text().strip()
        login = self.entry_login.text().strip()
        senha = self.entry_senha.text().strip()
        shares = [item.text() for item in selected_items]

        self.set_status("Mapeando pastas selecionadas...", "warning")
        self.btn_mapear.setEnabled(False)

        # Inicia a thread para mapear
        self.worker_mount = WorkerMountWorkspaces(ip, login, senha, shares, self.os_type)
        self.worker_mount.finished.connect(self.on_mount_finished)
        self.worker_mount.start()

    def on_mount_finished(self, success_count, error_str):
        self.btn_mapear.setEnabled(True)
        if error_str:
            msg = f"{success_count} pastas mapeadas.\nErros encontrados:\n{error_str}"
            self.set_status(msg, "danger")
            QMessageBox.critical(self, "Erros no Mapeamento", msg)
        else:
            self.set_status(f"Sucesso! {success_count} pastas mapeadas.", "success")

    def on_disconnect_click(self):
        reply = QMessageBox.question(
            self, "Confirmação", 
            "Tem certeza que deseja ejetar e desconectar todas as unidades de rede ativas?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.set_status("Desconectando unidades...", "warning")
            self.btn_desconectar.setEnabled(False)
            
            self.worker_disconnect = WorkerDisconnectAll(self.os_type)
            self.worker_disconnect.finished.connect(self.on_disconnect_finished)
            self.worker_disconnect.start()

    def on_disconnect_finished(self, success, msg):
        self.btn_desconectar.setEnabled(True)
        if success:
            self.set_status(msg, "success")
            QMessageBox.information(self, "Desconectado", msg)
        else:
            self.set_status("Erro ao desconectar.", "danger")
            QMessageBox.critical(self, "Erro", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Evitar o warning da fonte Roboto ausente no macOS/Windows e aumentar a fonte
    extra = {
        'font_family': 'Helvetica Neue' if platform.system() == 'Darwin' else 'Arial',
        'font_size': '16px',
    }
    
    # Aplica o tema Material Design Dark
    apply_stylesheet(app, theme='dark_teal.xml', extra=extra)
    
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())
