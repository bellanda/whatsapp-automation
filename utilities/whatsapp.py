import json
import os
import random
import time

import pyperclip
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants.config
import constants.paths
from utilities.win32 import copy_file_to_clipboard


class WhatsAppAutomation:
    def __init__(self, json_file):
        self.json_file = json_file
        self.driver = None
        self.wait = None
        self.contacts = []
        self.progress = self._load_progress()

    def _load_progress(self):
        """Carrega o progresso ou cria um novo se não existir"""
        try:
            if constants.paths.PROGRESS_FILE.exists():
                with open(constants.paths.PROGRESS_FILE, "r", encoding="utf-8") as f:
                    progress_data = json.load(f)
                    # Verificar se é o mesmo arquivo JSON
                    if progress_data.get("file_path") == str(self.json_file):
                        return progress_data
            # Se não existir ou for um arquivo diferente, criar novo progresso
            return {"file_path": str(self.json_file), "sent_indices": []}
        except Exception as e:
            print(f"Erro ao carregar progresso: {e}")
            return {"file_path": str(self.json_file), "sent_indices": []}

    def _save_progress(self, index):
        """Salva o progresso após enviar uma mensagem"""
        try:
            if index not in self.progress["sent_indices"]:
                self.progress["sent_indices"].append(index)

            with open(constants.paths.PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.progress, f)
        except Exception as e:
            print(f"Erro ao salvar progresso: {e}")

    def load_contacts(self):
        """Carrega os contatos do arquivo JSON"""
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                self.contacts = json.load(f)
            return True
        except Exception as e:
            print(f"Erro ao carregar o arquivo JSON: {e}")
            return False

    def all_contacts_processed(self):
        """Verifica se todos os contatos já foram processados"""
        if not self.contacts:
            return False

        total_contacts = len(self.contacts)
        processed_contacts = len(self.progress["sent_indices"])

        # Verifica se todos os índices estão no progresso
        return processed_contacts >= total_contacts and all(
            i in self.progress["sent_indices"] for i in range(total_contacts)
        )

    def initialize_driver(self):
        """Inicializa o driver do Chrome e abre o WhatsApp Web"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get("https://web.whatsapp.com")

        # Aguardar o usuário escanear o QR code
        print("Escaneie o código QR...")
        self.wait = WebDriverWait(self.driver, constants.config.QR_CODE_WAIT_TIME)
        self.wait.until(EC.presence_of_element_located((By.ID, "pane-side")))

        # Espera adicional após autenticação para garantir que a página carregou completamente
        time.sleep(constants.config.POST_AUTH_WAIT_TIME)

        try:
            self.driver.find_element(By.XPATH, "//div[text()='Continuar']").click()
        except Exception:
            pass

    def _safe_click_message_box(self):
        """Tenta clicar na caixa de mensagem de forma segura usando JavaScript"""
        try:
            # Espera a caixa de mensagem ficar visível
            message_box = self.wait.until(EC.presence_of_element_located((By.XPATH, constants.config.MESSAGE_BOX_XPATH)))

            # Tenta rolar até a caixa de mensagem para garantir visibilidade
            self.driver.execute_script("arguments[0].scrollIntoView(true);", message_box)
            time.sleep(1)

            # Tenta clicar diretamente
            try:
                message_box.click()
            except ElementClickInterceptedException:
                # Se houver interceptação, usa JavaScript para focar no elemento
                self.driver.execute_script("arguments[0].focus();", message_box)

            # Pequena pausa para garantir que o foco foi estabelecido
            time.sleep(0.5)
            return message_box
        except Exception as e:
            print(f"Erro ao clicar na caixa de mensagem: {e}")
            return None

    def send_messages(self, status_callback=None):
        """Envia mensagens para os contatos no arquivo JSON"""
        # Verifica se todos os contatos já foram processados antes de iniciar o navegador
        if self.all_contacts_processed():
            if status_callback:
                status_callback("Todos os contatos já foram processados. Nada a enviar.")
            return True

        if not self.contacts:
            if status_callback:
                status_callback("Nenhum contato carregado.")
            return False

        # Inicializa o driver somente se houver contatos para processar
        if not self.driver:
            self.initialize_driver()

        total = len(self.contacts)

        for i, contact in enumerate(self.contacts):
            # Verifica se já foi enviado
            if i in self.progress["sent_indices"]:
                if status_callback:
                    status_callback(f"Pulando contato {i + 1}/{total}: {contact.get('name')} - já enviado anteriormente")
                continue

            try:
                if status_callback:
                    status_callback(f"Enviando para {i + 1}/{total}: {contact.get('name')}")

                number = contact.get("number")
                message = contact.get("message", "")
                attachments = contact.get("attachments", [])

                # Validar número
                if not constants.config.PHONE_NUMBER_REGEX.match(number):
                    print(f"Número inválido: {number}")
                    continue

                # Remove caracteres não numéricos
                phone = "".join(filter(str.isdigit, number))

                # Abre a conversa
                self.driver.get(f"https://web.whatsapp.com/send?phone={phone}")

                # Aguarda a caixa de mensagem
                self.wait = WebDriverWait(self.driver, constants.config.MESSAGE_BOX_WAIT_TIME)
                self.wait.until(EC.presence_of_element_located((By.XPATH, constants.config.MESSAGE_BOX_XPATH)))

                # Espera adicional para garantir carregamento completo
                time.sleep(3)

                # Envia a mensagem de texto
                if message:
                    message_box = self._safe_click_message_box()
                    if message_box:
                        pyperclip.copy(message)
                        actions = ActionChains(self.driver)
                        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                        time.sleep(0.5)
                        actions.send_keys(Keys.ENTER).perform()

                # Envia os anexos um por um, exatamente como no código antigo
                for attachment in attachments:
                    if os.path.exists(attachment):
                        try:
                            copy_file_to_clipboard(attachment)

                            # Clica na caixa de mensagem para cada anexo
                            message_box = self._safe_click_message_box()
                            if message_box:
                                actions = ActionChains(self.driver)
                                actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                                # Aguarda o upload concluir
                                time.sleep(1.5)
                                actions.send_keys(Keys.ENTER).perform()
                        except Exception as e:
                            if status_callback:
                                status_callback(f"Erro ao enviar anexo {attachment}: {e}")
                            print(f"Erro ao enviar anexo {attachment}: {e}")

                # Salva o progresso
                self._save_progress(i)

                # Espera aleatória entre mensagens
                time.sleep(random.randint(constants.config.RANDOM_WAIT_MIN, constants.config.RANDOM_WAIT_MAX))

            except Exception as e:
                if status_callback:
                    status_callback(f"Erro ao enviar para {contact.get('name')}: {e}")
                print(f"Erro ao enviar para {contact.get('name')}: {e}")
                time.sleep(2)
                continue

        return True

    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()

    def reset_progress(self):
        """Reseta o progresso para começar do zero"""
        self.progress = {"file_path": str(self.json_file), "sent_indices": []}
        if os.path.exists(constants.paths.PROGRESS_FILE):
            os.remove(constants.paths.PROGRESS_FILE)
