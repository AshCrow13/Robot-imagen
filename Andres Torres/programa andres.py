import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
import serial
import time
from PIL import Image, ImageTk
import imutils
import cv2

class ProcesamientoImagenWebcam:
    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.root.resizable(True, True)
        self.root.title("Proyecto procesamiento de imagen con Webcam y conexion serial")
        # Configuración de comunicación serial
        self.serial_port = serial.Serial()

        self.serial_connected = False
        self.capture = None
        self.Captura = None
        self.img_mask = None
        self.img_aux = None
        self.bin_imagen = None
        self.thresh1 = None
        self.mask = None
        self.ImgRec = None

        self.rect_start = None
        self.rect_end = None
        self.rect_id = None

        self.create_widgets()

    def create_widgets(self):
        # Botones
        self.BCamara = tk.Button(self.root, text="Iniciar cámara", command=self.iniciar_camara)
        self.BCamara.place(x=60, y=330, width=90, height=23)
        self.BCapturar = tk.Button(self.root, text="Tomar foto", command=self.tomar_foto)
        self.BCapturar.place(x=250, y=330, width=91, height=23)
        self.BBinary = tk.Button(self.root, text="Umbralización", command=self.umbralizacion)
        self.BBinary.place(x=830, y=310, width=90, height=23)
        self.Bmanchas_g = tk.Button(self.root, text="Análisis de Manchas", command=self.manchas_g)
        self.Bmanchas_g.place(x=1400, y=200, width=140, height=23)
        self.root.bind("<Motion>", self.mostrar_coordenadas)
         # Botones de conexión serial
        self.BConectar = tk.Button(self.root, text="Conectar Serial", command=self.conectar_serial)
        self.BConectar.place(x=60, y=500, width=120, height=23)
        self.BDesconectar = tk.Button(self.root, text="Desconectar Serial", command=self.desconectar_serial)
        self.BDesconectar.place(x=250, y=500, width=120, height=23)
         # Botones para comandos seriales
        self.BEnviar = tk.Button(self.root, text="Enviar", command=self.enviar_serial)
        self.BEnviar.place(x=60, y=730, width=120, height=23)
        # Botón para limpiar textos
        self.BLimpiar = tk.Button(self.root, text="Limpiar textos", command=self.limpiar_textos_serial)
        self.BLimpiar.place(x=250, y=730, width=120, height=23)


        # Combobox para selección de puerto
        self.comboBox1 = ttk.Combobox(
            self.root,
            state="readonly",
            values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
        )
        self.comboBox1.set("COM1")
        self.comboBox1.place(x=60, y=530, width=140, height=22)

         # Cuadro de texto para ingresar comandos
        tk.Label(self.root, text="Comando a enviar:").place(x=60, y=560)
        self.TextComandos = tk.Text(self.root, height=5, width=50)
        self.TextComandos.place(x=60, y=590)
         # Cuadro de texto para mostrar respuestas
        tk.Label(self.root, text="Respuestas recibidas:").place(x=60, y=770)
        self.TextRespuestas = tk.Text(self.root, height=10, width=50, state='normal')
        self.TextRespuestas.place(x=60, y=800)
        # SpinBox
        self.numeroUmbra = tk.Spinbox(self.root, from_=0, to=255)
        self.numeroUmbra.place(x=930, y=310, width=42, height=22)

        #Datos de alumno, profesor y laboratorio
        self.alumno = tk.Label(self.root, text="Alumno: Andrés Torres")
        self.alumno.place(x=1450, y=930)
        self.profesor = tk.Label(self.root, text="Profesor: Luis Vera")
        self.profesor.place(x=1450, y=950)
        self.lab = tk.Label(self.root, text="Laboratorio CIM")
        self.lab.place(x=1450, y=970)

        # Logo Universidad
        self.logo = tk.PhotoImage(file="LogoUBB.png")
        self.logoUBB = ttk.Label(image=self.logo)
        self.logoUBB.place(x=1400, y=930)

        # Cuadros de Imagen grises
        self.LImagen = tk.Label(self.root, background="gray")
        self.LImagen.place(x=50, y=50, width=300, height=240)
        self.LImagenROI = tk.Label(self.root, background="gray")
        # Cuadro imagen recortada
        self.LImagenROI.place(x=720, y=50, width=300, height=240)
        self.UImagen = tk.Label(self.root, background="gray")
        self.UImagen.place(x=1040, y=50, width=301, height=240)
        self.LImagenRecorte = tk.Canvas(self.root, background="gray")
        self.LImagenRecorte.place(x=390, y=50, width=301, height=240)
        self.LImagenRecorte.bind("<Button-1>", self.on_button_press)
        self.LImagenRecorte.bind("<B1-Motion>", self.on_mouse_drag)
        self.LImagenRecorte.bind("<ButtonRelease-1>", self.on_button_release)

        # Cuadro de Texto de analisis de manchas
        self.CajaTexto = tk.Text(self.root, state="disabled")
        self.CajaTexto.place(x=1350, y=50, width=250, height=140)

        self.coordenadas = tk.Label(self.root, text="x = 0, y = 0")
        self.coordenadas.place(x=10, y=770, width=150, height=20)

        # Pasos
        tk.Label(self.root, text="Paso 1. Iniciar la cámara y tomar una foto").place(x=70, y=20)
        tk.Label(self.root, text="Paso 2. Pasar el cursor para recortar la imagen").place(x=400, y=20)
        tk.Label(self.root, text="Paso 3. Umbralizar, eligue un valor").place(x=730, y=20)
        tk.Label(self.root, text="Imagen umbralizada").place(x=1050, y=20)
        tk.Label(self.root, text="Paso 4. Analizar las manchas").place(x=1400, y=20)

        # Area de run pick and place
        # Añadir el marco "Pick and Place"
        self.pick_place_frame = tk.LabelFrame(self.root, text="RUN 'PICK AND PLACE'", padx=10, pady=10)
        self.pick_place_frame.place(x=730, y=450, width=440, height=300)

        # Campos del marco "Pick and Place"
        tk.Label(self.pick_place_frame, text="Part ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.part_id = ttk.Spinbox(self.pick_place_frame, from_=0, to=100)
        self.part_id.grid(row=0, column=1)

        tk.Label(self.pick_place_frame, text="Source ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.source_id = ttk.Spinbox(self.pick_place_frame, from_=1, to=100)
        self.source_id.grid(row=1, column=1)

        tk.Label(self.pick_place_frame, text="Source Index:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.source_index = ttk.Combobox(self.pick_place_frame, state="readonly", values=["1", "2", "3"])
        self.source_index.grid(row=1, column=3)

        tk.Label(self.pick_place_frame, text="Target ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.target_id = ttk.Spinbox(self.pick_place_frame, from_=1, to=100)
        self.target_id.grid(row=2, column=1)

        tk.Label(self.pick_place_frame, text="Target Index:").grid(row=2, column=2, sticky=tk.W, pady=5)
        self.target_index = ttk.Combobox(self.pick_place_frame, state="readonly", values=["1", "2"])
        self.target_index.grid(row=2, column=3)

        tk.Label(self.pick_place_frame, text="Note:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.note = ttk.Spinbox(self.pick_place_frame, from_=0, to=100)
        self.note.grid(row=3, column=1)

        # Botones para el marco
        tk.Button(self.pick_place_frame, text="OK", command=self.pick_place_ok).grid(row=4, column=1, pady=10)
        tk.Button(self.pick_place_frame, text="Cancel", command=self.pick_place_cancel).grid(row=4, column=2, pady=10)


    def iniciar_camara(self):
        self.capture = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        if self.capture is not None:
            ret, frame = self.capture.read()
            if ret:
                frame = imutils.resize(frame, width=310)
                frame = imutils.resize(frame, height=240)
                ImagenCamara = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(ImagenCamara)
                img = ImageTk.PhotoImage(image=im)
                self.LImagen.configure(image=img)
                self.LImagen.image = img
                self.LImagen.after(10, self.update_frame)
            else:
                self.LImagen.image = ""
                self.capture.release()

    def tomar_foto(self):
        # Capturar el cuadro actual de la cámara
        _, image = self.capture.read()
        frame = imutils.resize(image, width=310)
        frame = imutils.resize(frame, height=240)

        # Convertir a escala de grises
        self.CapturaG = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Mostrar la imagen en gris en el canvas de recorte
        imG = Image.fromarray(self.CapturaG)
        imgG = ImageTk.PhotoImage(image=imG)
        self.LImagenRecorte.create_image(0, 0, anchor=tk.NW, image=imgG)
        self.LImagenRecorte.image = imgG

        # También mostrar la imagen gris en el área de vista previa (opcional)
        self.GImagenROI.configure(image=imgG)
        self.GImagenROI.image = imgG

        print("Foto tomada y cargada en escala de grises.")

    def umbralizacion(self):
        if self.ImgRec is None:
            messagebox.showerror("Error", "Primero debe realizar un recorte en la imagen.")
            return

        # Umbralización de la imagen recortada
        valor = int(self.numeroUmbra.get())
        _, thresh1 = cv2.threshold(self.ImgRec, valor, 255, cv2.THRESH_BINARY)

        # Mostrar la imagen umbralizada
        Umbral = Image.fromarray(thresh1)
        Umbral = ImageTk.PhotoImage(image=Umbral)
        self.UImagen.configure(image=Umbral)
        self.UImagen.image = Umbral

        # Guardar la imagen umbralizada para análisis futuro
        self.thresh1 = thresh1


    def manchas_g(self):
        if self.thresh1 is None:
            messagebox.showerror("Error", "Primero debe aplicar la umbralización a la imagen recortada.")
            return

        # Análisis de manchas blancas
        num_pixels_blancos = cv2.countNonZero(self.thresh1)
        total_pixels = self.thresh1.size
        porcentaje_blancos = (num_pixels_blancos / total_pixels) * 100

        contornos_blancos, _ = cv2.findContours(self.thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cantidad_manchas_blancas = len(contornos_blancos)

        # Invertir la imagen para analizar manchas negras
        imagen_invertida = cv2.bitwise_not(self.thresh1)

        # Análisis de manchas negras
        num_pixels_negros = cv2.countNonZero(imagen_invertida)
        porcentaje_negros = (num_pixels_negros / total_pixels) * 100

        contornos_negros, _ = cv2.findContours(imagen_invertida, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cantidad_manchas_negras = len(contornos_negros)

        # Mostrar resultados en la interfaz
        Cadena = (
            f"--- Análisis de manchas ---\n"
            f"Manchas Blancas:\n"
            f" - Cantidad: {cantidad_manchas_blancas}\n"
            f" - Porcentaje del área: {round(porcentaje_blancos, 2)}%\n\n"
            f"Manchas Negras:\n"
            f" - Cantidad: {cantidad_manchas_negras}\n"
            f" - Porcentaje del área: {round(porcentaje_negros, 2)}%"
        )

        self.CajaTexto.configure(state='normal')
        self.CajaTexto.delete(1.0, tk.END)
        self.CajaTexto.insert(1.0, Cadena)
        self.CajaTexto.configure(state='disabled')

        print("Análisis de manchas completado.")



    def on_button_press(self, event):
        self.rect_start = (event.x, event.y)
        if self.rect_id:
            self.LImagenRecorte.delete(self.rect_id)
        self.rect_id = self.LImagenRecorte.create_rectangle(self.rect_start[0], self.rect_start[1], self.rect_start[0], self.rect_start[1], outline='red')

    def on_mouse_drag(self, event):
        self.rect_end = (event.x, event.y)
        self.LImagenRecorte.coords(self.rect_id, self.rect_start[0], self.rect_start[1], self.rect_end[0], self.rect_end[1])

    def on_button_release(self, event):
        self.rect_end = (event.x, event.y)
        self.recortar()

    def recortar(self):
        if self.CapturaG is not None and self.rect_start and self.rect_end:
            Vx1, Vy1 = self.rect_start
            Vx2, Vy2 = self.rect_end

            # Asegurarse de que las coordenadas sean válidas
            if Vx1 >= Vx2 or Vy1 >= Vy2:
                print("Error: Las coordenadas de recorte no son válidas.")
                return

            # Asegurarse de que las coordenadas estén dentro del rango de la imagen
            height, width = self.CapturaG.shape
            Vx1, Vx2 = max(0, Vx1), min(width, Vx2)
            Vy1, Vy2 = max(0, Vy1), min(height, Vy2)

            # Realizar el recorte
            self.ImgRec = self.CapturaG[Vy1:Vy2, Vx1:Vx2]
            Im = Image.fromarray(self.ImgRec)
            ImRec = ImageTk.PhotoImage(image=Im)
            self.LImagenROI.configure(image=ImRec)
            self.LImagenROI.image = ImRec
            print("Imagen recortada correctamente.")


    def mostrar_coordenadas(self, event):
        self.coordenadas['text'] = f'x = {event.x}    y = {event.y}'

    def mostrar_coordenadas(self, event):
        x, y = event.x, event.y
        self.coordenadas.configure(text=f"x = {x}, y = {y}")

    # Funciones de conexión serial
    def conectar_serial(self):
        if not self.serial_port.isOpen():
            try:
                self.serial_port.baudrate = 9600
                self.serial_port.bytesize = 8
                self.serial_port.parity = serial.PARITY_NONE
                self.serial_port.stopbits = serial.STOPBITS_ONE
                self.serial_port.port = self.comboBox1.get()
                self.serial_port.open()
                self.serial_connected = True
                messagebox.showinfo("Éxito", "Conexión serial establecida.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def desconectar_serial(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.serial_connected = False
            messagebox.showinfo("Éxito", "Conexión serial cerrada.")

    def enviar_serial(self):
        if self.serial_connected:
            mensaje = self.TextComandos.get("1.0", tk.END).strip()
            if mensaje:
                try:
                    # Enviar el mensaje por el puerto serial
                    self.serial_port.write(mensaje.encode() + b"\r")
                    time.sleep(0.5)

                    # Leer la respuesta del puerto serial
                    recibido = self.serial_port.read_all().decode()

                    # Agregar la respuesta al cuadro de respuestas
                    self.TextRespuestas.insert(tk.END, f"> {mensaje}\n{recibido}\n")

                    # Limpiar el cuadro de comandos
                    self.TextComandos.delete("1.0", tk.END)
                except Exception as e:
                    # Mostrar errores en un cuadro de mensaje emergente
                    messagebox.showerror("Error", f"No se pudo enviar el mensaje: {e}")
            else:
                messagebox.showerror("Error", "Debe ingresar un comando para enviar.")
        else:
            messagebox.showerror("Error", "Conexión serial no establecida.")

    def limpiar_textos_respuestas(self):
        """Limpia el cuadro de texto donde se muestran las respuestas."""
        self.TextRespuestas.delete("1.0", tk.END)

    def limpiar_textos_serial(self):
        self.TextComandos.delete("1.0", tk.END)

    def pick_place_ok(self):
        # Obtener valores del formulario
        part_id = self.part_id.get()
        source_id = self.source_id.get()
        source_index = self.source_index.get()
        target_id = self.target_id.get()
        target_index = self.target_index.get()
        note = self.note.get()

        # Verificar que todos los campos hayan sido llenados
        if not all([part_id, source_id, source_index, target_id, target_index, note]):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        # Lista de comandos y respuestas esperadas
        comandos_y_respuestas = [
            ("RUN PCPLC", "ID?"),  # RUN PCPLC, espera "ID?"
            (part_id, None),       # Enviar ID
            (source_id, None),     # Enviar SOURCE_ID
            (source_index, None),  # Enviar SOURCE_INDEX
            ("RUN GT001", "Target ID?"),  # RUN GT001, espera "Target ID?"
            (target_id, None),     # Enviar TARGET_ID
            (target_index, None),  # Enviar TARGET_INDEX
            ("RUN PT012", "Note?"),# RUN PT012, espera "Note?"
            (note, None),          # Enviar note
            ("%START 110000", None),  # Ejecutar START
            ("%FINISH 110000", None), # Ejecutar FINISH
            ("%END 110000", None),    # Finalizar
        ]

        if self.serial_connected:
            try:
                for comando, respuesta_esperada in comandos_y_respuestas:
                    # Enviar el comando al puerto serial
                    self.serial_port.write((comando + "\r").encode())
                    time.sleep(1)  # Esperar por la respuesta

                    # Leer la respuesta del terminal
                    recibido = self.serial_port.read_all().decode()

                    # Mostrar en consola y en la interfaz para depuración
                    print(f"Comando enviado: {comando}")
                    print(f"Respuesta recibida: {recibido}")
                    self.TextRecibidos.insert("1.0", recibido + "\n")

                    # Verificar si la respuesta coincide con lo esperado
                    if respuesta_esperada and respuesta_esperada not in recibido:
                        messagebox.showerror("Error", f"Respuesta inesperada: {recibido}")
                        return
                messagebox.showinfo("Pick and Place", "Comandos enviados exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo completar el flujo: {e}")
        else:
            messagebox.showerror("Error", "Conexión serial no establecida.")

    def pick_place_cancel(self):
        # Limpiar valores del formulario
        self.part_id.delete(0, tk.END)
        self.source_id.delete(0, tk.END)
        self.source_index.set("")
        self.target_id.delete(0, tk.END)
        self.target_index.set("")
        self.note.delete(0, tk.END)
        messagebox.showinfo("Pick and Place", "Formulario restablecido.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcesamientoImagenWebcam(root)
    root.mainloop()