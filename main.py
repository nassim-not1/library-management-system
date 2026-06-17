import sys
from PySide6.QtWidgets import QApplication, QDialog
from views.main_window import MainWindow
from views.login_dialog import LoginDialog

def main():
    app = QApplication(sys.argv)
    
    from views.style import LIGHT_THEME_QSS
    app.setStyleSheet(LIGHT_THEME_QSS)
    
    while True:
        login_dialog = LoginDialog()
        if login_dialog.exec() != QDialog.Accepted:
            break

        window = MainWindow(login_dialog.authenticated_user)
        window.is_logged_out = False
        
        def handle_logout():
            window.is_logged_out = True
            window.close()
            
        window.logout_requested.connect(handle_logout)
        window.show()
        
        app.exec()
        
        # Si la fenêtre a été fermée sans demander de déconnexion (ex: bouton X), on quitte.
        if not getattr(window, 'is_logged_out', False):
            break

if __name__ == "__main__":
    main()
