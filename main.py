import tkinter as tk

from utilities.gui import WhatsAppAutomationGUI


def main():
    """Função principal que inicia a aplicação"""
    root = tk.Tk()
    WhatsAppAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
