import ctypes
from ctypes import wintypes

import win32clipboard
import win32con

# Carrega o kernel32 com suporte a GetLastError
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Declarações de tipos para GlobalAlloc, GlobalLock, GlobalUnlock e GlobalFree
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = ctypes.c_void_p

kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p

kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.restype = wintypes.BOOL

kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
kernel32.GlobalFree.restype = ctypes.c_void_p


# Estrutura DROPFILES conforme a API do Windows
class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


def copy_file_to_clipboard(file_path: str):
    """
    Copia file_path para a área de transferência como CF_HDROP.
    """
    # Certifique-se de usar barras invertidas
    file_path = file_path.replace("/", "\\")

    # Prepara a lista de arquivos (UTF-16LE, dupla terminação)
    files = file_path + "\0"
    unicode_bytes = (files + "\0").encode("utf-16le")

    # Prepara DROPFILES
    drop = DROPFILES()
    drop.pFiles = ctypes.sizeof(DROPFILES)
    drop.pt_x = drop.pt_y = 0
    drop.fNC = False
    drop.fWide = True

    total_size = ctypes.sizeof(DROPFILES) + len(unicode_bytes)
    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040

    # Aloca e trava memória
    hGlobal = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, total_size)
    if not hGlobal:
        raise ctypes.WinError(ctypes.get_last_error())

    ptr = kernel32.GlobalLock(hGlobal)
    if not ptr:
        kernel32.GlobalFree(hGlobal)
        raise ctypes.WinError(ctypes.get_last_error())

    # Copia DROPFILES + lista de caminhos
    ctypes.memmove(ptr, ctypes.byref(drop), ctypes.sizeof(DROPFILES))
    ctypes.memmove(ptr + ctypes.sizeof(DROPFILES), unicode_bytes, len(unicode_bytes))
    kernel32.GlobalUnlock(hGlobal)

    # Cola na área de transferência
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_HDROP, hGlobal)
    finally:
        win32clipboard.CloseClipboard()


if __name__ == "__main__":
    caminho = r"C:\Users\gusta\Downloads\4k-anime-wallpaper-whatspaper-1_WFHD.jpg"
    copy_file_to_clipboard(caminho)
    print("Arquivo copiado! Agora pressione Ctrl+V no WhatsApp Web.")
