from tkinter import *  
from tkinter import ttk 
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import datetime
import time


debounce_id = None


# Creiamo la finestra
root = Tk()
root.title('galleria - film preferiti')
root.geometry('1000x700')  # Aumentata per contenere tutti gli elementi
root.configure(bg="#5a5e59")
root.minsize(800, 600)
#root.resizable(False, False)
try:
    root.iconbitmap('./slide.ico')
except:
    print("Icona non trovata o non compatibile su questo sistema.")

# Percorso base del progetto (dove si trova lo script)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Dizionario generi -> cartelle
GENERI_CARTELLE = {
    "Azione": os.path.join(PROJECT_DIR, "Azione"),
    "Avventura": os.path.join(PROJECT_DIR, "Avventura"),
    "Animazione": os.path.join(PROJECT_DIR, "Animazione"),
    "Commedia": os.path.join(PROJECT_DIR, "Commedia")
}

# Verifica e crea le cartelle se non esistono
for genere, cartella in GENERI_CARTELLE.items():
    if not os.path.exists(cartella):
        os.makedirs(cartella)
        print(f"Creata cartella: {cartella}")

#Visualizza le icone sulla barra di stato
icon_images = {}
try:
    icon_images["info"] = ImageTk.PhotoImage(Image.open("info.png").resize((24, 24)))
    icon_images["success"] = ImageTk.PhotoImage(Image.open("success.png").resize((24, 24)))
    icon_images["error"] = ImageTk.PhotoImage(Image.open("error.png").resize((24, 24)))
    img = Image.open("icon.png")
except Exception as e:
    print("Errore caricamento icone barra stato:", e)


def carica_immagini_da_cartella(cartella, nome_genere):
    """Funzione helper per caricare immagini da una cartella"""
    if not os.path.exists(cartella):
        aggiorna_status(f"Cartella {nome_genere} non trovata", "error")
        messagebox.showerror("Errore", f"Cartella {nome_genere} non trovata!\nPercorso: {cartella}")
        return False
    
    try:
        global image_paths, current_image_index
        estensioni_valide = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
        
        # Ottieni tutte le immagini valide nella cartella
        all_images = [
            os.path.join(cartella, f) 
            for f in os.listdir(cartella) 
            if f.lower().endswith(estensioni_valide)
        ]

        if not all_images:
            aggiorna_status(f"Nessuna immagine in {nome_genere}", "error")
            messagebox.showwarning("Attenzione", f"Nessuna immagine trovata in {nome_genere}!")
            return False
        
        # Nome dell'immagine rappresentativa del genere (in minuscolo per il confronto)
        genere_img_name = f"{nome_genere.lower()}.png"
        
        # Creiamo una nuova lista ordinata con l'immagine del genere per prima
        image_paths = []
        
        # Prima aggiungiamo l'immagine del genere se esiste
        for img_path in all_images:
            if os.path.basename(img_path).lower() == genere_img_name:
                image_paths.append(img_path)
                break
        
        # Poi aggiungiamo tutte le altre immagini
        for img_path in all_images:
            if os.path.basename(img_path).lower() != genere_img_name:
                image_paths.append(img_path)
        
        # Verifica finale che ci siano immagini
        if not image_paths:
            image_paths = all_images  # Fallback alle immagini originali
            
        current_image_index = 0
        mostra_immagine()
        aggiorna_status(f"Caricate {len(image_paths)} immagini {nome_genere}", "success")
        
        # Debug - visualizza l'ordine delle immagini caricate
        print(f"Ordine immagini {nome_genere}:")
        for i, path in enumerate(image_paths):
            print(f"{i+1}: {os.path.basename(path)}")
            
        return True
        
    except Exception as e:
        aggiorna_status(f"Errore caricamento {nome_genere}: {str(e)}", "error")
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
        return False



# Manteniamo gli stessi nomi di funzione richiesti
def carica_cartella_azione():
    """Carica le immagini dalla cartella Azione"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Azione"], "Azione")

def carica_cartella_avventura():
    """Carica le immagini dalla cartella Avventura"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Avventura"], "Avventura")

def carica_cartella_animazione():
    """Carica le immagini dalla cartella Animazione"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Animazione"], "Animazione")

def carica_cartella_commedia():
    """Carica le immagini dalla cartella Commedia"""
    carica_immagini_da_cartella(GENERI_CARTELLE["Commedia"], "Commedia")



# Funzionalità viewer immagini
image_paths = []
current_image_index = 0
tk_img = None  # Per evitare garbage collection dell'immagine

def carica_immagini():
    """Carica immagini da una cartella selezionata"""
    global image_paths, current_image_index, original_images, current_genere
    
    cartella = filedialog.askdirectory(title="Seleziona una cartella con immagini")
    if not cartella:
        aggiorna_status("Caricamento annullato", "info")
        return
    
    try:
        estensioni_valide = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
        image_paths = sorted([
            os.path.join(cartella, f) 
            for f in os.listdir(cartella) 
            if f.lower().endswith(estensioni_valide)
        ])

        if not image_paths:
            aggiorna_status("Nessuna immagine trovata", "error")
            messagebox.showwarning("Attenzione", "Nessuna immagine trovata nella cartella selezionata!")
            return
            
        current_image_index = 0
        original_images = image_paths.copy()
        current_genere = "Personalizzato"  # Impostato quando si carica manualmente
        mostra_immagine()
        aggiorna_status(f"Caricate {len(image_paths)} immagini dalla cartella", "success")
        
        # Forza l'aggiornamento delle informazioni
        update_image_info(image_paths[current_image_index])
        
    except Exception as e:
        aggiorna_status(f"Errore caricamento immagini: {str(e)}", "error")
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
    
# Aggiorna anche la funzione mostra_immagine per assicurarsi che update_image_info venga chiamata correttamente
def mostra_immagine():
    global tk_img
    if not image_paths or current_image_index >= len(image_paths):
        print("Nessuna immagine da mostrare.")
        return

    img_path = image_paths[current_image_index]
    print(f"Mostrando immagine: {img_path}")
    img = Image.open(img_path)

    # Prendi la larghezza/altezza attuale del widget image_label
    label_width = image_label.winfo_width()
    label_height = image_label.winfo_height()

    if label_width < 10 or label_height < 10:
        # Se la finestra è ancora in caricamento, imposta valori predefiniti
        label_width = 530
        label_height = 390

    # Ridimensiona l'immagine alle dimensioni attuali del label
    img = img.resize((label_width, label_height), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(img.copy())

    image_label.config(image=tk_img)

    # Aggiorna info immagine
    file_name = os.path.basename(img_path)
    # Usa la query corrente per aggiornare lo status bar
    query = entry_ricerca.get().strip().lower()
    generi_files = ["azione.png", "avventura.png", "animazione.png", "commedia.png"]
    
    if not query and file_name.lower() in generi_files:
        # Per le immagini di genere, mostra un messaggio specifico
        aggiorna_status(f"Visualizzazione: {file_name} (immagine principale del genere {os.path.splitext(file_name)[0].capitalize()})")
    elif query and os.path.splitext(file_name)[0].lower().startswith(query):
        # Conta quanti file iniziano con il prefisso di ricerca
        matching_count = sum(1 for p in image_paths if os.path.splitext(os.path.basename(p))[0].lower().startswith(query))
        aggiorna_status(f"Visualizzazione: {file_name} (match con '{query}', {matching_count} immagini trovate)")
    else:
        aggiorna_status(f"Visualizzazione: {file_name} ({current_image_index + 1} di {len(image_paths)})")
    
    update_image_info(img_path)


def update_image_info(img_path):
    """Aggiorna il pannello informativo con i dettagli dell'immagine"""
    global current_genere, search_results
    
    # Ottieni le informazioni del file
    file_name = os.path.basename(img_path)
    file_size = os.path.getsize(img_path) / 1024  # KB
    file_ext = os.path.splitext(img_path)[1].upper().replace(".", "")
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(img_path)).strftime('%d/%m/%Y %H:%M')
    resolution = Image.open(img_path).size
    
    # Determina il testo per la posizione
    if len(image_paths) == 1:
        pos_text = "1 di 1 immagine"
    else:
        pos_text = f"{current_image_index + 1} di {len(image_paths)} immagini"  # Modificato qui
    
    info_text = (
        f"• Nome: {file_name}\n\n"
        f"• Genere: {current_genere if current_genere else 'Personalizzato'}\n\n"  # Modificato qui
        f"• Formato: {file_ext}\n\n"
        f"• Dimensione: {file_size:.1f} KB\n\n"
        f"• Risoluzione: {resolution[0]}×{resolution[1]} px\n\n"
        f"• Data creazione: {creation_date}\n\n"
        f"• Posizione: {pos_text}\n\n"
        f"• Percorso: {os.path.dirname(img_path)}"
    )
    
    info_label.config(text=info_text)

def immagine_successiva():
    global current_image_index
    if image_paths:
        current_image_index = (current_image_index + 1) % len(image_paths)
        print(f"Indice immagine successiva: {current_image_index}")  # Debug
        mostra_immagine()

def immagine_precedente():
    global current_image_index
    if image_paths:
        print(f"Indice prima del cambio (precedente): {current_image_index}")  # Debug    
        if current_image_index == 0:
            current_image_index = len(image_paths) -1
        else:
            current_image_index -= 1
        print(f"Indice dopo il cambio (precedente): {current_image_index}")  # Debug
        mostra_immagine()

def aggiorna_status(testo, tipo="info"):
    colori = {
        "info": ("#dddddd", "black"),
        "success": ("#d4edda", "green"),
        "error": ("#f8d7da", "red")
    }
    bg, fg = colori.get(tipo, ("#dddddd", "black"))
    
    # Imposta colore e testo
    status_frame.config(bg=bg)
    status_bar.config(text=testo, bg=bg, fg=fg)
    status_icon.config(image=icon_images.get(tipo), bg=bg)


# Frame per il pannello informativo a sinistra
info_frame = Frame(root, bg="#3c285e")
info_frame.place(relx=0.03, rely=0.35, relwidth=0.40, relheight=0.57)

# Etichetta per il titolo del pannello
Label(info_frame, text="INFORMAZIONI IMMAGINE", bg="#3c285e", fg="white", 
      font=("Arial", 12, "bold")).pack(pady=(0, 10))

# Etichetta per le informazioni dettagliate
info_label = Label(info_frame, text="Nessuna immagine caricata", 
                  bg="#3c285e", fg="white", font=("Arial", 10), 
                  justify=LEFT, anchor="nw", wraplength=280)
info_label.pack(fill=BOTH, expand=True)


# Titolo genere
titolo_genere = Label(root, text="🎬 Seleziona un genere 🎬", bg="#5a5e59", fg="white", font=("Helvetica", 14, "bold"))
titolo_genere.place(relx=0.45, rely=0.21, relwidth=0.52, relheight=0.05)


# Bottoni genere
btn_specs = [
    ("Azione", 0.45, carica_cartella_azione, "#b22222", "yellow"),
    ("Avventura", 0.58, carica_cartella_avventura, "#228b22", "black"),
    ("Animazione", 0.71, carica_cartella_animazione, "#2422a8", "red"),
    ("Commedia", 0.84, carica_cartella_commedia, "#a8228b", "blue")
]

for text, relx, command, bg_color, fg_color in btn_specs:
    Button(root, text=text, command=command, bg=bg_color, fg=fg_color, activebackground="#1ebaba", activeforeground="#fafcfc").place(relx=relx, rely=0.30, relwidth=0.13, relheight=0.05)


# Text box
text_box = Text(root)
text_box.place(relx=0.03, rely=0.07, relwidth=0.46, relheight=0.10)


def apri_file():
    filetypes = (
        ('file di testo', '*.txt'),
        ('tutti i file', '*.*')
    )
    filename = filedialog.askopenfilename(title="Apri un file", initialdir="/", filetypes=filetypes) 
    if filename:  # Controlla se è stato selezionato un file
        print(f"File aperto: {filename}")
        try:
            with open(filename, 'r') as f:
                data = f.read()
                text_box.delete('1.0', END)  # Pulisce la Text box
                text_box.insert(END, data)   # Inserisce il contenuto
        except Exception as e:
            print(f"Errore nella lettura del file: {e}")

        try:
            f_save = filedialog.asksaveasfile(mode="w", title="Salva file", defaultextension=".txt")
            if f_save:
                data_to_write = "HO SOSTITUITO IL FILE" 
                f_save.write(data_to_write)
                f_save.close()
        except Exception as e:
            print(f"Errore nel salvataggio del file: {e}")


#bottone mostra istruzioni
def mostra_istruzioni():
    istruzioni = (
        "📌 Istruzioni per l'utilizzo dell'app 'Galleria - Film Preferiti':\n"
        "\n"
        "1. Puoi caricare anche immagini da una cartella a scelta con il pulsante 'Carica Immagini'.\n"
        "\n"
        "2. Clicca su uno dei pulsanti di genere (Azione, Avventura, Animazione, Commedia) per caricare le immagini dei film.\n"
        "\n"
        "3. Usa i pulsanti '← Precedente' e 'Successiva →' per scorrere tra le immagini.\n"
        "\n"
        "4. Visualizza le informazioni dettagliate del film nel pannello a sinistra: nome file, dimensioni, risoluzione, data e percorso.\n"
        "\n"
        "5. Per aprire un file di testo e modificarlo, usa il pulsante 'Apri'.\n"
        "\n"
        "6. Nell'area di testo, al di sopra del pulsante 'Apri', si possono visualizzare, i contenuti inseriti o già presenti, all'interno dei file di testo.\n"
        "\n" 
        "7. Utilizza la barra di ricerca in alto per cercare un'immagine per nome tra tutte quelle caricate o trovate nel sistema.\n"
        "\n"
        "8. Puoi selezionare uno o più formati immagine (JPG, PNG, GIF, ICO, ecc.) tramite le checkbox accanto alla barra di ricerca per affinare la ricerca.\n"
        "\n"
        "9. Nel menu in alto trovi varie funzionalità:\n"
        "   - File: Apri, Esci\n"
        "   - Modifica: Taglia, Copia, Incolla\n"
        "   - Visualizza: Debug, Terminale\n"
        "   - Guida: Istruzioni, Info app\n"
        "   - Altro: Aggiornamenti, Note\n"
        "\n"
        "💡 Consiglio: assicurati che le immagini siano nei formati supportati (.jpg, .png, .gif, .ico, ecc.)."
    )
    messagebox.showinfo("Istruzioni", istruzioni)



# Carica un'icona (assicurati che il file esista)
try:
    icona = PhotoImage(file="instruction_icon.png")  # Sostituisci con il tuo file
    bottone_popup = ttk.Button(root, text=" Istruzioni", image=icona, compound="left", command=mostra_istruzioni)
except Exception as e:
    print("Icona non trovata o errore nel caricamento:", e)
    bottone_popup = ttk.Button(root, text="Istruzioni", command=mostra_istruzioni)

bottone_popup.place(relx=0.76, rely=0.12, relwidth=0.12, relheight=0.05, anchor="nw")


# Bottone Apri
bottone = ttk.Button(root, text="Apri", command=apri_file)
bottone.place(relx=0.03, rely=0.21, relwidth=0.12, relheight=0.06)


# creato un Menu bar in alto 
menubar = Menu(root)
root.config(menu=menubar)  

File_menu = Menu(menubar, tearoff=0)
Modifica_menu = Menu(menubar, tearoff=0)
Visualizza_menu = Menu(menubar, tearoff=0)
Guida_menu = Menu(menubar, tearoff=0)
Altro_menu = Menu(menubar)

file_altro_submenu = Menu(File_menu, tearoff=0)
file_altro_submenu.add_command(label='Disponibilità Aggiornamenti')
file_altro_submenu.add_command(label='About galleria-film preferiti')

File_menu.add_command(label='Nuovo', command=root.quit)
File_menu.add_separator()
File_menu.add_command(label='Apri', command=root.quit)
File_menu.add_separator()
File_menu.add_cascade(label='Altro', menu=file_altro_submenu)
File_menu.add_separator()
File_menu.add_command(label='Exit', command=root.quit)


Modifica_menu.add_command(label='Taglia', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_command(label='Copia', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_cascade(label='Incolla', command=root.quit)
Modifica_menu.add_separator()
Modifica_menu.add_command(label='Cerca', command=root.quit)


Visualizza_menu.add_command(label='Apri finestra', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_command(label='Esegui', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_cascade(label='Debug', command=root.quit)
Visualizza_menu.add_separator()
Visualizza_menu.add_command(label='Terminale', command=root.quit)


Guida_menu.add_command(label='FAQ', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_command(label='Estensioni', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_cascade(label='Guarda Licenza', command=root.quit)
Guida_menu.add_separator()
Guida_menu.add_command(label='Video Introduttivo', command=root.quit)


menubar.add_cascade(label='File', menu=File_menu)
menubar.add_cascade(label='Modifica', menu=Modifica_menu)
menubar.add_cascade(label='Visualizza', menu=Visualizza_menu)
menubar.add_cascade(label='Guida', menu=Guida_menu)


# ---------- SEZIONE IMAGE VIEWER ----------
Button(root, text="Carica Immagini", bg="orange", command=carica_immagini).place(relx=0.21, rely=0.21, relwidth=0.12, relheight=0.06 )
Button(root, text="← Precedente", command=immagine_precedente).place(relx=0.45, rely=0.95, anchor="sw")
Button(root, text="Successiva →", command=immagine_successiva).place(relx=0.97, rely=0.95, anchor="se")


# Image viewer
image_label = Label(root, bg="white")
image_label.place(relx=0.45, rely=0.35, relwidth=0.52, relheight=0.56)
image_label.bind("<Configure>", lambda e: mostra_immagine())


#Barra di stato  
status_frame = Frame(root, bd=1, relief=SUNKEN, bg="#dddddd")
status_frame.pack(side=BOTTOM, fill=X)

status_icon = Label(status_frame, bg="#dddddd")
status_icon.pack(side=LEFT, padx=5)

status_bar = Label(status_frame, text="Benvenuto nella galleria!", anchor=W, bg="#dddddd", fg="black")
status_bar.pack(side=LEFT, fill=X, expand=True)


def inizializza_formati():
    """Inizializza le variabili per i checkbox dei formati immagine"""
    global formati_var
    formati_var = {
        'JPEG': IntVar(value=1),  # Selezionato di default
        'PNG': IntVar(value=1),   # Selezionato di default
        'ICO': IntVar(value=0),   # Non selezionato di default
        'BMP': IntVar(value=0)    # Non selezionato di default
    }

def cerca_immagini(realtime=False):
    query = entry_ricerca.get().strip().lower()
    
    if not query:
        reset_ricerca()
        return

    global image_paths, current_image_index
    
    if not hasattr(cerca_immagini, 'original_images'):
        cerca_immagini.original_images = image_paths.copy()
    
    risultati = []
    exact_match_index = None
    
    for i, img_path in enumerate(cerca_immagini.original_images):
        nome_file = os.path.splitext(os.path.basename(img_path))[0].lower()
        
        if query == nome_file:  # Trovato match esatto
            exact_match_index = i
            risultati = [img_path]
            break
        elif query in nome_file:  # Trovato match parziale
            risultati.append(img_path)
    
    if exact_match_index is not None:
        image_paths = risultati
        current_image_index = 0
        if not realtime:
            aggiorna_status(f"Trovato match esatto: {os.path.basename(image_paths[0])}", "success")
    elif risultati:
        image_paths = risultati
        current_image_index = 0
        if not realtime:
            aggiorna_status(f"Trovati {len(risultati)} risultati", "success")
    else:
        if not realtime:
            aggiorna_status("Nessun risultato trovato", "error")
        return
    
    mostra_immagine()
    
    # Per la ricerca in tempo reale, mostra un messaggio diverso
    if realtime:
        if len(query) >= 3:
            aggiorna_status(f"Ricerca in tempo reale: {len(risultati)} risultati per '{query}'", "info")

            
def reset_ricerca():
    """Resetta la ricerca e mostra tutte le immagini"""
    global image_paths, current_image_index
    
    # Ripristina tutte le immagini se esistono quelle originali
    if hasattr(cerca_immagini, 'original_images'):
        image_paths = cerca_immagini.original_images.copy()
        current_image_index = 0
        mostra_immagine()
        aggiorna_status("Ricerca resettata - Mostro tutte le immagini", "info")
        entry_ricerca.delete(0, END)  # Pulisce il campo di ricerca


def ridimensiona_finestra():
    root.geometry("1200x800")
    aggiorna_status("Finestra ridimensionata a 1200x800", "info")

bottone_ridimensiona = Button(root, text="Ridimensiona", bg="#a86832", fg="white",
                              activebackground="#a832a8", command=ridimensiona_finestra)
bottone_ridimensiona.place(relx=0.58, rely=0.12, relwidth=0.11, relheight=0.05)

def cerca_immagini_con_debounce(event=None):
    global debounce_id, current_image_index

    # Annulla eventuale chiamata precedente
    if debounce_id is not None:
        root.after_cancel(debounce_id)

    query = entry_ricerca.get().strip().lower()
    
    # Se la query è vuota, resetta la ricerca
    if not query:
        reset_ricerca()
        return
    
    # Se ci sono almeno 3 caratteri, cerca in tempo reale
    if len(query) >= 3:
        debounce_id = root.after(150, lambda: cerca_immagini(True))  # Riduci il debounce a 150ms per risposta più rapida


# Inizializza formati
inizializza_formati()

# 1. Configurazione iniziale
SEARCH_BAR_INIT_WIDTH = 500  # Larghezza iniziale in pixel
SEARCH_BAR_MIN_WIDTH = 300   # Larghezza minima

# 2. Frame principale per contenere tutti gli elementi
frame_ricerca_principale = Frame(root, bg="#5a5e59")
frame_ricerca_principale.place(relx=0.97, rely=0.02, anchor="ne")

# 3. Frame superiore per l'etichetta e le checkbox dei formati
frame_superiore = Frame(frame_ricerca_principale, bg="#5a5e59")
frame_superiore.pack(side=TOP, fill=X, pady=(0, 3))

# Etichetta "Formati:"
label_formati = Label(frame_superiore, text="Formati:", 
                     bg="#5a5e59", fg="white", 
                     font=("Arial", 8, "bold"))
label_formati.pack(side=LEFT, padx=(0, 2))

# Frame per i checkbox
frame_checkbox = Frame(frame_superiore, bg="#5a5e59")
frame_checkbox.pack(side=LEFT, fill=X)

# Creazione dei checkbox in modalità compatta
for formato in formati_var:
    cb = Checkbutton(frame_checkbox, text=formato, variable=formati_var[formato],
                   bg="#5a5e59", fg="white", selectcolor="#3c285e",
                   font=("Arial", 8), padx=2)
    cb.pack(side=LEFT, padx=3)

# 4. Frame inferiore per la barra di ricerca
frame_ricerca_completo = Frame(frame_ricerca_principale, bg="#5a5e59")
frame_ricerca_completo.pack(side=BOTTOM, fill=X)

# 5. Barra di ricerca espandibile
frame_ricerca = Frame(frame_ricerca_completo, bg="#3c285e", bd=1, relief=SOLID)
frame_ricerca.pack(side=LEFT, fill=BOTH, expand=True)

entry_ricerca = Entry(frame_ricerca, bg="white", fg="black", bd=0,
                     font=("Arial", 9))
entry_ricerca.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=3)

# Aggiunta evento Invio per cercare
entry_ricerca.bind("<Return>", lambda event: cerca_immagini())
entry_ricerca.bind("<KeyRelease>", cerca_immagini_con_debounce)


# 6. Bottoni cerca e reset
bottone_ricerca = Button(frame_ricerca, text="🔍", command=cerca_immagini,
                        bg="#86961a", fg="white", bd=0, width=3,
                        activebackground="#768a16", font=("Arial", 10))
bottone_ricerca.pack(side=RIGHT, fill=Y)

# Bottone reset separato
bottone_reset = Button(frame_ricerca_completo, text="↺", command=reset_ricerca,
                      bg="#c44536", fg="white", bd=0, width=3,
                      activebackground="#b23b2e", font=("Arial", 10))
bottone_reset.pack(side=LEFT, fill=Y, padx=(3, 0))

# 7. Gestione ridimensionamento mantenendo le checkbox sempre visibili
def adatta_ricerca(event=None):
    win_width = root.winfo_width()
    
    # Protezione contro dimensioni non valide durante l'inizializzazione
    if win_width <= 1:
        return
    
    # Calcolo della larghezza in base allo spazio disponibile
    if win_width < 800:
        new_width = max(SEARCH_BAR_MIN_WIDTH, win_width * 0.4)
    else:
        new_width = SEARCH_BAR_INIT_WIDTH
    
    # Applica la nuova larghezza mantenendo la posizione
    frame_ricerca_principale.config(width=int(new_width))
    
    # Aggiorna immediatamente
    frame_ricerca_principale.update_idletasks()

# 8. Configurazione eventi
root.bind("<Configure>", adatta_ricerca)


# Inizializzazione
adatta_ricerca()

# Posizionamento pulsante istruzioni sotto la barra di ricerca, adattato per essere più responsive
bottone_popup.place(relx=0.97, rely=0.12, relwidth=0.15, relheight=0.05, anchor="ne")



# Avvia la finestra
root.mainloop()    