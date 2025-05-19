import re

# Regex para validação de números de telefone
PHONE_NUMBER_REGEX = re.compile(r"\+?\d{1,3}[-.\s]?\d{1,14}[-.\s]?\d{1,14}[-.\s]?\d{1,14}")

# XPATHs do WhatsApp Web - atualizados para maior compatibilidade
MESSAGE_BOX_XPATH = '//*[@contenteditable="true" and @data-tab="10"]'
SEND_BUTTON_XPATH = '//*[@data-icon="send"]'

# Tempos de espera (em segundos)
QR_CODE_WAIT_TIME = 1000
MESSAGE_BOX_WAIT_TIME = 30  # Aumentado para dar mais tempo para a página carregar
RANDOM_WAIT_MIN = 3
RANDOM_WAIT_MAX = 8

# Tempo de espera extra após autenticação
POST_AUTH_WAIT_TIME = 5
