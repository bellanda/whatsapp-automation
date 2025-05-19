# WhatsApp Automação

Aplicação para automação de envio de mensagens para contatos do WhatsApp a partir de um arquivo JSON.

## Requisitos

- Python 3.7+
- Google Chrome
- WebDriver do Chrome compatível com sua versão do navegador
- Módulos Python requeridos listados em `requirements.txt`

## Instalação

1. Clone o repositório ou baixe o código fonte
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Verifique se você tem o Chrome WebDriver instalado e configurado corretamente no PATH

## Formato do arquivo JSON

O aplicativo lê os contatos e mensagens a partir de um arquivo JSON com o seguinte formato:

```json
[
  {
    "name": "Nome do Contato",
    "number": "+5511999999999",
    "message": "Olá, como vai?",
    "attachments": ["C:\\caminho\\para\\imagem.jpg", "C:\\caminho\\para\\documento.pdf"]
  },
  {
    "name": "Outro Contato",
    "number": "+5511988888888",
    "message": "Outra mensagem personalizada",
    "attachments": []
  }
]
```

## Como usar

1. Execute o aplicativo:

```bash
python main.py
```

2. Na interface gráfica, clique em "Procurar" para selecionar o arquivo JSON
3. Clique em "Iniciar Automação" para começar
4. Escaneie o código QR com seu celular para autenticar no WhatsApp Web
5. O aplicativo enviará as mensagens automaticamente para os contatos especificados

## Funcionalidades

- Envio automatizado de mensagens via WhatsApp Web
- Suporte a imagens e outros tipos de anexos
- Retomada de onde parou em caso de falha
- Interface gráfica simples e amigável
- Acompanhamento em tempo real do progresso de envio

## Observações

- O WhatsApp pode limitar o número de mensagens enviadas em um curto período de tempo para evitar spam
- Use com responsabilidade e evite enviar mensagens em massa para destinatários que não consentiram com o recebimento
