import tkinter as tk
from tkinter import messagebox, ttk
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pyperclip

def enter():
    url = entrada_url.get().strip()
    
    if not url:
        messagebox.showwarning("Error", "Por favor ingresa una URL")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result_listbox.delete(0, tk.END)
        
        # 1. Título de la página
        if soup.title:
            result_listbox.insert(tk.END, "=== TÍTULO DE LA PÁGINA ===")
            result_listbox.insert(tk.END, soup.title.string)
            result_listbox.insert(tk.END, "")
        
        # 2. Titulares (h1-h3)
        result_listbox.insert(tk.END, "=== TITULARES ===")
        for level in ['h1', 'h2', 'h3']:
            headers = soup.find_all(level)
            if headers:
                result_listbox.insert(tk.END, f"--- {level.upper()} ---")
                for header in headers:
                    result_listbox.insert(tk.END, f"• {header.get_text(strip=True)}")
        result_listbox.insert(tk.END, "")
        
        # 3. Párrafos principales (primeros 5)
        result_listbox.insert(tk.END, "=== PÁRRAFOS PRINCIPALES ===")
        paragraphs = soup.find_all('p')[:5]  
        for idx, p in enumerate(paragraphs, 1):
            text = p.get_text(strip=True)
            if len(text) > 100:  
                text = text[:100] + "..."
            result_listbox.insert(tk.END, f"{idx}. {text}")
        result_listbox.insert(tk.END, "")
        
        # 4. Enlaces importantes (los primeros 10)
        result_listbox.insert(tk.END, "=== ENLACES DESTACADOS ===")
        links = soup.find_all('a', href=True)[:10]
        domain = urlparse(url).netloc
        for idx, link in enumerate(links, 1):
            text = link.get_text(strip=True) or "[sin texto]"
            href = link['href']
            if not href.startswith('http'):
                href = f"https://{domain}{href}"
            result_listbox.insert(tk.END, f"{idx}. {text[:30]}... → {href}")
        
        # 5. Imágenes (primeras 3)
        result_listbox.insert(tk.END, "")
        result_listbox.insert(tk.END, "=== IMÁGENES ===")
        images = soup.find_all('img')[:3]
        for idx, img in enumerate(images, 1):
            src = img.get('src', '') or img.get('data-src', '')
            alt = img.get('alt', '') or "[sin texto alternativo]"
            if src:
                if not src.startswith('http'):
                    src = f"https://{domain}{src}"
                result_listbox.insert(tk.END, f"{idx}. {alt[:30]}... → {src}")
        
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudo acceder a la URL:\n{str(e)}")
        result_listbox.insert(tk.END, "Error al conectar con la URL")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{str(e)}")
        result_listbox.insert(tk.END, "Error en el proceso de scraping")

def copy():
    try:
        selection = result_listbox.get(result_listbox.curselection())
        if selection:
            pyperclip.copy(selection)
            messagebox.showinfo("Copiado", "Texto copiado al portapapeles")
    except tk.TclError:
        messagebox.showwarning("Advertencia", "No hay nada seleccionado")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar: {str(e)}")

# Configuración de la interfaz
win = tk.Tk()
win.title("Web Scraper Avanzado")
win.geometry("1024x768")

# Frame superior
top_frame = tk.Frame(win)
top_frame.pack(pady=20)

title = tk.Label(top_frame, text="Web Scraper", font=("arial", 24))
title.pack()

# Frame de entrada
input_frame = tk.Frame(win)
input_frame.pack(pady=10)

tk.Label(input_frame, text="URL:").pack(side=tk.LEFT)
entrada_url = tk.Entry(input_frame, width=50)
entrada_url.pack(side=tk.LEFT, padx=5)
enter_b = tk.Button(input_frame, text="Buscar", command=enter)
enter_b.pack(side=tk.LEFT)

# Frame de resultados
result_frame = tk.Frame(win)
result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Scrollbar
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Listbox para resultados
result_listbox = tk.Listbox(
    result_frame, 
    yscrollcommand=scrollbar.set,
    font=("Consolas", 10),
    selectbackground="#4CAF50",
    selectforeground="white",
    activestyle="none",
    height=25
)
result_listbox.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=result_listbox.yview)

copy_b = tk.Button(win, text="Copiar", command=copy)
copy_b.pack(pady=10)

win.mainloop()
