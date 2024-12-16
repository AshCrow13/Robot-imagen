import tkinter as tk
from tkinter import messagebox, simpledialog, END
from tkinter.filedialog import askopenfilename
from turtle import width
from PIL import Image, ImageTk
import imutils
import time
import os
import cv2
import glob


class analisisTemplate:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1600x900")
        self.root.resizable(0, 0)
        self.root.title("Analisis de patrones")
        self.capture = None
        self.CapturaG = None
        self.ImgRec = None
        self.thresh1 = None
        self.rect_start = None
        self.rect_end = None
        self.rect_id = None

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.liberar_recursos)

    def create_widgets(self):
        # Botones para procesamiento de imagen
        self.BCamara = tk.Button(self.root, text="Iniciar cámara", command=self.iniciar_camara)
        self.BCamara.place(x=60, y=330, width=90, height=23)
        self.BCapturar = tk.Button(self.root, text="Tomar foto", command=self.tomar_foto)
        self.BCapturar.place(x=250, y=330, width=91, height=23)
        self.BBinary = tk.Button(self.root, text="Umbralización", command=self.umbralizacion)
        self.BBinary.place(x=830, y=310, width=90, height=23)
        self.Bmanchas_g = tk.Button(self.root, text="Análisis de Manchas", command=self.manchas_g)
        self.Bmanchas_g.place(x=1400, y=410, width=140, height=23)

        # Botones para cargar imagen
        self.BSubirImagen = tk.Button(self.root, text="Subir Imagen", command=self.subir_imagen)
        self.BSubirImagen.place(x=60, y=370, width=90, height=23)

        # Botón para analizar patrones
        self.BAnalizar = tk.Button(self.root, text="Analizar Patrones", command=self.analizar_patrones)
        self.BAnalizar.place(x=250, y=370, width=120, height=23)

        # Cuadros de Imagen
        self.LImagen = tk.Label(self.root, background="gray")
        self.LImagen.place(x=50, y=50, width=300, height=240)
        self.LImagenROI = tk.Label(self.root, background="gray")
        self.LImagenROI.place(x=720, y=50, width=300, height=240)
        self.UImagen = tk.Label(self.root, background="gray")
        self.UImagen.place(x=1040, y=50, width=301, height=240)
        self.LImagenRecorte = tk.Canvas(self.root, background="gray")
        self.LImagenRecorte.place(x=390, y=50, width=301, height=240)
        self.LImagenRecorte.bind("<Button-1>", self.on_button_press)
        self.LImagenRecorte.bind("<B1-Motion>", self.on_mouse_drag)
        self.LImagenRecorte.bind("<ButtonRelease-1>", self.on_button_release)
        self.ImagenSubida = tk.Label(self.root , background="gray")
        self.ImagenSubida.place(x=50, y=400, width=300, height=240)

        # SpinBox para umbralización
        self.numeroUmbra = tk.Spinbox(self.root, from_=0, to=255)
        self.numeroUmbra.place(x=930, y=310, width=42, height=22)

        # Cuadro de Texto de análisis de manchas
        self.CajaTexto = tk.Text(self.root, state="disabled")
        self.CajaTexto.place(x=1350, y=50, width=250, height=300)

        # Indicador de estado
        self.label_estado = tk.Label(self.root, text="", fg="blue")
        self.label_estado.place(x=700, y=400, width=300, height=20)

    def mostrar_estado(self, mensaje):
        self.label_estado.configure(text=mensaje)
        self.root.update_idletasks()

    def liberar_recursos(self):
        if self.capture:
            self.capture.release()
            self.capture = None
        self.root.destroy()

    def iniciar_camara(self):
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise ValueError("No se pudo abrir la cámara. Verifique que esté conectada.")
            self.update_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar la cámara: {e}")

    def update_frame(self):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                frame = imutils.resize(frame, width=310, height=240)
                ImagenCamara = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(ImagenCamara)
                img = ImageTk.PhotoImage(image=im)
                self.LImagen.configure(image=img)
                self.LImagen.image = img
                self.LImagen.after(10, self.update_frame)

    def tomar_foto(self):
        try:
            ret, image = self.capture.read()
            if not ret:
                raise ValueError("No se pudo capturar la foto. Asegúrese de que la cámara esté funcionando.")

            frame = imutils.resize(image, width=310, height=240)
            self.CapturaG = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            nombre_imagen = simpledialog.askstring("Guardar Foto", "Ingrese el nombre para la foto (sin extensión):")
            if not nombre_imagen or not nombre_imagen.isalnum():
                raise ValueError("El nombre ingresado no es válido. Debe ser alfanumérico.")

            filepath = f"{nombre_imagen}.jpg"
            cv2.imwrite(filepath, frame)
            messagebox.showinfo("Foto guardada", f"La foto se guardó correctamente como {filepath}")

            imG = Image.fromarray(self.CapturaG)
            imgG = ImageTk.PhotoImage(image=imG)
            self.LImagenRecorte.create_image(0, 0, anchor=tk.NW, image=imgG)
            self.LImagenRecorte.image = imgG

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error inesperado: {e}")

    def umbralizacion(self):
        if self.ImgRec is None:
            messagebox.showerror("Error", "Primero debe realizar un recorte en la imagen.")
            return

        try:
            # Solicitar nombre para la imagen umbralizada
            nombre_imagen_umbralizada = simpledialog.askstring(
                "Guardar Umbralización", "Ingrese el nombre para la imagen umbralizada (sin extensión):"
            )
            if not nombre_imagen_umbralizada or not nombre_imagen_umbralizada.isalnum():
                raise ValueError("El nombre ingresado no es válido. Debe ser alfanumérico.")

            valor = int(self.numeroUmbra.get())
            _, self.thresh1 = cv2.threshold(self.ImgRec, valor, 255, cv2.THRESH_BINARY)

            # Guardar la imagen umbralizada
            archivo_umbralizada = f"{nombre_imagen_umbralizada}.jpg"
            cv2.imwrite(archivo_umbralizada, self.thresh1)

            # Mostrar en la interfaz
            Umbral = Image.fromarray(self.thresh1)
            Umbral = ImageTk.PhotoImage(image=Umbral)
            self.UImagen.configure(image=Umbral)
            self.UImagen.image = Umbral

            messagebox.showinfo("Imagen Guardada", f"Imagen umbralizada guardada como {archivo_umbralizada}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error: {e}")


    def manchas_g(self):
        if self.thresh1 is None:
            messagebox.showerror("Error", "Primero debe aplicar la umbralización a la imagen recortada.")
            return

        self.mostrar_estado("Analizando manchas, por favor espere...")
        self.root.after(100)

        try:
            # Solicitar nombre para la imagen de manchas analizadas
            nombre_imagen_manchas = simpledialog.askstring(
                "Guardar Análisis de Manchas", "Ingrese el nombre para la imagen analizada (sin extensión):"
            )
            if not nombre_imagen_manchas or not nombre_imagen_manchas.isalnum():
                raise ValueError("El nombre ingresado no es válido. Debe ser alfanumérico.")
            
            # Análisis de manchas
            num_pixels_blancos = cv2.countNonZero(self.thresh1)
            total_pixels = self.thresh1.size
            porcentaje_blancos = (num_pixels_blancos / total_pixels) * 100

            contornos_blancos, _ = cv2.findContours(self.thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cantidad_manchas_blancas = len(contornos_blancos)

            imagen_invertida = cv2.bitwise_not(self.thresh1)
            num_pixels_negros = cv2.countNonZero(imagen_invertida)
            porcentaje_negros = (num_pixels_negros / total_pixels) * 100

            contornos_negros, _ = cv2.findContours(imagen_invertida, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cantidad_manchas_negras = len(contornos_negros)

            # Crear una copia de la imagen con los contornos dibujados
            imagen_con_contornos = self.ImgRec.copy()
            cv2.drawContours(imagen_con_contornos, contornos_blancos, -1, (255, 255, 255), 2)
            cv2.drawContours(imagen_con_contornos, contornos_negros, -1, (0, 0, 0), 2)

            # Generar nombres únicos para las imágenes
            timestamp = int(time.time())
            archivo_umbralizada = f"umbralizada_{timestamp}.jpg"
            archivo_manchas = f"{nombre_imagen_manchas}_{timestamp}_manchas_analizadas.jpg"

            # Guardar las imágenes con nombres únicos
            cv2.imwrite(archivo_umbralizada, self.thresh1)
            cv2.imwrite(archivo_manchas, imagen_con_contornos)

            # Buscar la imagen más parecida usando histogramas
            imagen_umbralizada = cv2.imread(archivo_umbralizada, cv2.IMREAD_GRAYSCALE)
            max_similitud = 0
            imagen_mas_parecida = None

            # Iterar sobre imágenes en la carpeta actual
            for filepath in glob.glob("*.jpg"):
                if filepath == archivo_umbralizada:
                    continue

                # Leer la imagen a comparar
                imagen_comparar = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                if imagen_comparar is None:
                    continue

                # Calcular el histograma de ambas imágenes
                hist_umbralizada = cv2.calcHist([imagen_umbralizada], [0], None, [256], [0, 256])
                hist_comparar = cv2.calcHist([imagen_comparar], [0], None, [256], [0, 256])

                # Normalizar los histogramas para que sean comparables
                cv2.normalize(hist_umbralizada, hist_umbralizada)
                cv2.normalize(hist_comparar, hist_comparar)

                # Comparar los histogramas usando correlación
                similitud = cv2.compareHist(hist_umbralizada, hist_comparar, cv2.HISTCMP_CORREL)

                # Actualizar la imagen más parecida
                if similitud > max_similitud:
                    max_similitud = similitud
                    imagen_mas_parecida = filepath

            # Determinar el mensaje según las manchas analizadas
            if porcentaje_negros > 80:
                mensaje_objeto = "No se detectó un objeto en la imagen (más del 80% es negro)."
            elif cantidad_manchas_blancas > cantidad_manchas_negras:
                mensaje_objeto = "Objeto sin forma detectado."
            else:
                mensaje_objeto = "Objeto detectado con forma."

            # Mostrar resultados
            Cadena = (
                f"--- Análisis de manchas ---\n"
                f"Manchas Blancas:\n"
                f" - Cantidad: {cantidad_manchas_blancas}\n"
                f" - Porcentaje del área: {round(porcentaje_blancos, 2)}%\n\n"
                f"Manchas Negras:\n"
                f" - Cantidad: {cantidad_manchas_negras}\n"
                f" - Porcentaje del área: {round(porcentaje_negros, 2)}%\n\n"
                f"Imágenes guardadas:\n"
                f" - Umbralización: {archivo_umbralizada}\n"
                f" - Análisis de manchas: {archivo_manchas}\n\n"
                f"Imagen más parecida: {imagen_mas_parecida if imagen_mas_parecida else 'No se encontraron coincidencias.'}\n"
                f" - Similitud: {max_similitud:.2f}\n"
                f"Resultado: {mensaje_objeto}"
            )

            self.CajaTexto.configure(state='normal')
            self.CajaTexto.delete(1.0, END)
            self.CajaTexto.insert(1.0, Cadena)
            self.CajaTexto.configure(state='disabled')

            self.mostrar_estado("Análisis de manchas completado.")
        except Exception as e:
            self.mostrar_estado("Error durante el análisis de manchas.")
            messagebox.showerror("Error", f"Error inesperado: {e}")


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

            if Vx1 >= Vx2 or Vy1 >= Vy2:
                messagebox.showerror("Error", "Las coordenadas de recorte no son válidas.")
                return

            height, width = self.CapturaG.shape
            Vx1, Vx2 = max(0, Vx1), min(width, Vx2)
            Vy1, Vy2 = max(0, Vy1), min(height, Vy2)

            self.ImgRec = self.CapturaG[Vy1:Vy2, Vx1:Vx2]
            Im = Image.fromarray(self.ImgRec)
            ImRec = ImageTk.PhotoImage(image=Im)
            self.LImagenROI.configure(image=ImRec)
            self.LImagenROI.image = ImRec

    def analizar_patrones(self):

        try:
            mejor_similitud = 0
            mejor_imagen = None
            mejor_coordenadas = None

            # Obtener la lista de todas las imágenes en el directorio actual
            imagenes = glob.glob("*.jpg") + glob.glob("*.jpeg") + glob.glob("*.png")

            if not imagenes:
                messagebox.showinfo("Sin Imágenes", "No se encontraron imágenes en la carpeta actual.")
                return

            # Iterar sobre cada imagen y aplicar coincidencia de plantillas
            for imagen_path in imagenes:
                imagen_actual = cv2.imread(imagen_path, cv2.IMREAD_GRAYSCALE)
                if imagen_actual is None:
                    continue

                # Asegurarse de que la imagen sea lo suficientemente grande
                if imagen_actual.shape[0] < self.ImgRec.shape[0] or imagen_actual.shape[1] < self.ImgRec.shape[1]:
                    continue

                # Aplicar coincidencia de plantillas
                resultado = cv2.matchTemplate(imagen_actual, self.ImgRec, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(resultado)

                # Guardar los mejores resultados
                if max_val > mejor_similitud:
                    mejor_similitud = max_val
                    mejor_imagen = imagen_path
                    mejor_coordenadas = max_loc
                    mejor_match = imagen_actual.copy()

            # Verificar si se encontró alguna coincidencia válida
            if mejor_imagen:
                # Dibujar el rectángulo en la imagen con mejor coincidencia
                top_left = mejor_coordenadas
                h, w = self.ImgRec.shape
                bottom_right = (top_left[0] + w, top_left[1] + h)

                cv2.rectangle(mejor_match, top_left, bottom_right, 255, 2)

                # Mostrar la imagen con el rectángulo
                im_rect = Image.fromarray(mejor_match)
                img_rect = ImageTk.PhotoImage(image=im_rect)
                self.UImagen.configure(image=img_rect)
                self.UImagen.image = img_rect

                # Mostrar información del mejor resultado
                precision = mejor_similitud * 100
                messagebox.showinfo(
                    "Resultado del Análisis",
                    f"Mejor coincidencia encontrada en: {mejor_imagen}\nPrecisión: {precision:.2f}%"
                )

                print(f"Mejor coincidencia en: {mejor_imagen}")
                print(f"Precisión: {precision:.2f}%")
            else:
                messagebox.showinfo("Sin Coincidencias", "No se encontraron coincidencias para la región recortada.")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis de patrones: {e}")



    def subir_imagen(self):
        filepath = askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not filepath:
            return

        # Leer la imagen en escala de grises
        self.CapturaG = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if self.CapturaG is None:
            messagebox.showerror("Error", "No se pudo cargar la imagen seleccionada.")
            return

        # Mostrar la imagen original en "Imagen Subida"
        resized_image = cv2.resize(self.CapturaG, (300, 240))
        imG = Image.fromarray(resized_image)
        imgG = ImageTk.PhotoImage(image=imG)
        self.ImagenSubida.configure(image=imgG)
        self.ImagenSubida.image = imgG

        # Mostrar la imagen en el área de recorte para manipulación
        imG_recorte = Image.fromarray(self.CapturaG)
        imgG_recorte = ImageTk.PhotoImage(image=imG_recorte)
        self.LImagenRecorte.create_image(0, 0, anchor=tk.NW, image=imgG_recorte)
        self.LImagenRecorte.image = imgG_recorte



if __name__ == "__main__":
    root = tk.Tk()
    app = analisisTemplate(root)
    root.mainloop()