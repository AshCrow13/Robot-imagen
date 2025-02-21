import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import numpy as np
import imutils
import cv2
from datetime import datetime
import os

#Ventana
ventana = tk.Tk()
ventana.geometry("1500x700")
ventana.title("Analisis de patrones y Comparación de Imágenes") 

imageToShow = None
Captura = None
Captura_threshold =None
camara_activada = False
boton_iniciar_visible = False

# Elegir carpeta para imagenes
def seleccionar_carpeta():
    global personPath
    selected_path = filedialog.askdirectory(title="Seleccionar carpeta")
    if selected_path:
        personPath = selected_path
        messagebox.showinfo("Carpeta seleccionada", f"Carpeta configurada: {personPath}")

# Función para mostrar la cámara umbralizada en tiempo real
def mostrar_camara_umbralizada():
    global capture, LImagenUmbralizada, Captura_threshold
    if capture is not None:
        ret, frame = capture.read()
        if ret: 
            # Cambiar a escala de grises y aplicar umbralización
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)            
            # Obtener el valor del Spinbox, con un valor predeterminado en caso de error
            try:
                umb = int(SGray.get())
            except ValueError:
                umb = 0            
            _, threshold_frame = cv2.threshold(gray_frame, umb, 255, cv2.THRESH_BINARY)
            # Redimensionar la imagen al tamaño del Label
            threshold_frame_resized = cv2.resize(threshold_frame, (300, 240), interpolation=cv2.INTER_AREA)
            # Guardar la imagen umbralizada en Captura
            Captura_threshold = threshold_frame
            # Recortar la imagen umbralizada utilizando los valores de los sliders
            x = SX.get()
            y = SY.get()
            w = SW.get()
            h = SH.get()
            threshold_frame = threshold_frame[y:h, x:w]
            # Convertir a formato compatible con Tkinter
            im = Image.fromarray(threshold_frame_resized)
            img_umbralizada = ImageTk.PhotoImage(image=im)
            # Mostrar la imagen umbralizada en el nuevo Label
            LImagenUmbralizada.configure(image=img_umbralizada)
            LImagenUmbralizada.image = img_umbralizada
            LImagenUmbralizada.after(100, mostrar_camara_umbralizada)
        else:
            LImagenUmbralizada.image = ""
            capture.release()
            messagebox.showerror("Error", "No se pudo capturar ningún fotograma.")

def camara():
    global capture, camara_activada, boton_iniciar_visible
    if not camara_activada:
        try:
            capture = cv2.VideoCapture(0) #----ELEGIR QUE CAMARA USAR----#
            iniciar()
            mostrar_camara_umbralizada()  # Iniciar la vista umbralizada en tiempo real
            camara_activada = True
            boton_iniciar_visible = True
        except Exception as e:
            messagebox.showerror("Error al inicializar la cámara: " + str(e))
    else:
        if capture is not None:
            capture.release()
            boton_iniciar_visible = False
        LImagen.configure(image="")
        LImagenUmbralizada.configure(image="")  # Limpiar el Label de la imagen umbralizada
        messagebox.showinfo("Información", "Cámara desactivada")
        camara_activada = False

# La función iniciar permite inicializar la cámara y actualizar continuamente la imagen capturada en un widget
def iniciar():
    global capture    
    if capture is not None:  # Verificamos si la cámara está correctamente inicializada
        # Controlar la visibilidad del botón "BCapturar" según el estado de 'boton_iniciar_visible'
        if boton_iniciar_visible:  
            BCapturar.place(x=250, y=310, width=91, height=23)
        else:
            BCapturar.place_forget()  # Oculta el botón "BCapturar"        
        ret, frame = capture.read()  
        if ret == True:
            # Redimensionar el fotograma para ajustarlo al tamaño deseado
            frame = imutils.resize(frame, width=311)  
            frame = imutils.resize(frame, height=241)            
            # Convertir el fotograma de BGR (formato predeterminado de OpenCV) a RGB
            ImagenCamara = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convertir el array de la imagen a un formato compatible con Tkinter
            im = Image.fromarray(ImagenCamara)
            img = ImageTk.PhotoImage(image=im)            
            # Actualizar el widget 'LImagen' con la nueva imagen capturada
            LImagen.configure(image=img)  
            LImagen.image = img           
            LImagen.after(100, iniciar)# Programar la ejecución recurrente
        else:
            LImagen.image = ""  
            capture.release()  # Liberar los recursos de la cámara
            messagebox.showerror(message="No se pudo capturar ningún fotograma.")


#Funcion Captura permite capturar la fotografia al presionar el boton
def Capturar():
    global valor, Captura, Captura_threshold
    # Asignar el objeto de captura de la cámara
    camara = capture    
    # Capturar un fotograma de la cámara
    _, frame = camara.read()    
    # Redimensionar la imagen capturada a un tamaño de altura 221 píxeles
    frame = imutils.resize(frame, height=221)    
    
    Captura = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)# Convertir la imagen capturada a formato RGB (de BGR a RGB)    
    im = Image.fromarray(Captura)# Convertir la imagen RGB a formato que Tkinter puede manejar
    img = ImageTk.PhotoImage(image=im)    
    # Mostrar la imagen RGB en el primer Label (LImagen)
    LImagen.configure(image=img)
    LImagen.image = img 
    
    # Convertir la imagen a escala de grises (de BGR a GRAY)
    Captura = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    
    # Convertir la imagen en escala de grises a formato compatible con Tkinter
    im = Image.fromarray(Captura)
    img = ImageTk.PhotoImage(image=im)    
    # Mostrar la imagen en escala de grises en el segundo Label (LImagen2)
    LImagen2.configure(image=img)
    LImagen2.image = img  # Mantener una referencia de la imagen    
    valor = 2

# Estas funciones permiten recortar la imagen a tiempo real
def actualizar_area_recorte(_=None):
    global imageToShow, valor, Captura
    if imageToShow is not None or Captura is not None:
        x = SX.get()
        y = SY.get()
        w = SW.get()
        h = SH.get()
        # Inicializar con un valor predeterminado
        imagen_recortada = None
        if valor == 0:
            imagen_recortada = imageToShow.copy()
        else:
            imagen_recortada = Captura.copy()
            # Crear una máscara negra del mismo tamaño que la imagen original
        mascara_negra = np.zeros_like(imagen_recortada)
            # Establecer el área seleccionada
        mascara_negra[y:h, x:w] = 255
            # Superponer la imagen original con el área seleccionada
        imagen_recortada = cv2.bitwise_and(imagen_recortada, mascara_negra)
        im = Image.fromarray(imagen_recortada)
        img_recortada = ImageTk.PhotoImage(image=im)
        LImagen2.configure(image=img_recortada)
        LImagen2.image = img_recortada

# Función para recortar imagen
def recortar_imagen():
    global imageToShow, valor, Captura
    x = SX.get()
    y = SY.get()
    w = SW.get()
    h = SH.get()
    if valor == 0:
        imagen_recortada = imageToShow[y:h, x:w]
    else:
        imagen_recortada = Captura[y:h, x:w]
    # Superponer la imagen recortada en la posición deseada
    im = Image.fromarray(imagen_recortada)
    img_recortada = ImageTk.PhotoImage(image=im)
    LImagen2.configure(image=img_recortada)
    LImagen2.image = img_recortada
    return(imagen_recortada)

# Esta funcion permite umbralizar la imagen para encontrar manchas
def rgb():
    # Recortar la imagen antes de analizar las manchas
    recortada = recortar_imagen()
    # Luego proceder con el análisis de las manchas
    umb = int(SGray.get())
    img_mask = cv2.inRange(recortada, umb,255)
    img_aux = 255 - img_mask
    img_mask = Image.fromarray(img_mask)
    img_mask = ImageTk.PhotoImage(image=img_mask)
    LImagenManchas.configure(image=img_mask)
    LImagenManchas.image = img_mask    
    _, bin_imagen = cv2.threshold(img_aux, umb, 255, cv2.THRESH_BINARY_INV)
    # Contar el número de píxeles con manchas
    num_pixels_con_manchas = cv2.countNonZero(bin_imagen)
    # Calcular el porcentaje de manchas
    porcentaje_manchas = 100 - (num_pixels_con_manchas / bin_imagen.size) * 100
    # Contornos
    contornos,_ = cv2.findContours(img_aux, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    area = 0
    # Verificar si num_pixels_con_manchas es diferente de cero antes de dividir
    if num_pixels_con_manchas != 0:
        area = (bin_imagen.size / (num_pixels_con_manchas / bin_imagen.size))
    else:
        area = 0
    # Cantidad de contornos
    num_formas = len(contornos)
    Cadena = f"Cantidad de manchas detectada:{num_formas}\nArea Mancha: {area}\nPorcentaje de manchas:{round(porcentaje_manchas,2)}%"
    CajaTexto.configure(state='normal')
    CajaTexto.delete(1.0, tk.END)
    CajaTexto.insert(1.0, Cadena)
    CajaTexto.configure(state='disabled')
    return img_aux

#Funcion Guardar 
def guardar_imagen():
    recortada = rgb()
    if recortada is None:
        messagebox.showerror("Error", "No hay imagen para guardar.")
        return

    # Pedir al usuario el nombre del archivo
    nombre_archivo = simpledialog.askstring("Guardar imagen", "Ingrese el nombre del archivo:")
    if not nombre_archivo:
        messagebox.showinfo("Cancelado", "No se guardó la imagen.")
        return

    # Agregar extensión al nombre si no se proporcionó
    if not nombre_archivo.lower().endswith(".jpg"):
        nombre_archivo += ".jpg"

    # Crear la ruta completa del archivo
    ruta_completa = os.path.join(personPath, nombre_archivo)

    try:
        # Guardar la imagen recortada
        cv2.imwrite(ruta_completa, 255 - recortada)
        messagebox.showinfo("Éxito", f"Imagen guardada como: {ruta_completa}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")

# Función para cargar imágenes de la carpeta
def cargar_imagenes_carpeta():
    global img_folder, image_path, personPath
    try:
        image_path = personPath
        if image_path:
            img_folder = [os.path.join(image_path, f) for f in os.listdir(image_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if not img_folder:
                messagebox.showwarning("Advertencia", "No se encontraron imágenes en la carpeta seleccionada.")
            else:
                messagebox.showinfo("Información", f"Se han cargado {len(img_folder)} imágenes de la carpeta.")
    except Exception as e:
        messagebox.showerror(message="Error al cargar las imágenes: " + str(e))

def preprocesar_imagen(img, size=(300, 240)):
    """ Preprocesa la imagen para comparación: escala de grises y redimensionamiento. """
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    img_resized = cv2.resize(img_gray, size)
    return img_resized


def comparar_con_imagen(descriptors_cam, keypoints_cam, img_carpeta):
    """
    Compara los descriptores y keypoints de la imagen capturada con una imagen de la carpeta.
    """
    sift = cv2.SIFT_create()  # Usar SIFT para una comparación más robusta
    img_carpeta_proc = preprocesar_imagen(img_carpeta)
    keypoints_folder, descriptors_folder = sift.detectAndCompute(img_carpeta_proc, None)

    if descriptors_folder is None:
        return None, float('inf')  # Si no hay descriptores, retornar puntaje alto

    # Comparador de características
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors_cam, descriptors_folder, k=2)

    # Filtrar coincidencias usando RANSAC y test de ratio de Lowe
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:  # Test de ratio
            good_matches.append(m)

    if len(good_matches) > 4:  # Verificar suficientes coincidencias
        src_pts = np.float32([keypoints_cam[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints_folder[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Calcular la homografía y filtrar coincidencias usando RANSAC
        _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        inliers = np.sum(mask)
        score = 1 / (inliers + 1)  # El puntaje se basa en el número de inliers

        return img_carpeta_proc, score
    else:
        return None, float('inf')  # Puntaje alto si no hay suficientes coincidencias


def comparar_imagenes():
    """
    Compara la imagen capturada con las imágenes de la carpeta usando SIFT y RANSAC.
    """
    global Captura_threshold, img_folder

    if Captura_threshold is None or not img_folder:
        messagebox.showwarning("Advertencia", "Por favor, capture una imagen y cargue las imágenes de la carpeta.")
        return

    # Preprocesar la imagen capturada
    img_captura_proc = preprocesar_imagen(Captura_threshold)
    sift = cv2.SIFT_create()
    keypoints_cam, descriptors_cam = sift.detectAndCompute(img_captura_proc, None)

    if descriptors_cam is None:
        messagebox.showerror("Error", "No se encontraron características en la imagen capturada.")
        return

    # Comparar con las imágenes de la carpeta
    mejor_coincidencia = None
    mejor_score = float('inf')
    mejor_nombre = None

    for img_path in img_folder:
        img_carpeta = cv2.imread(img_path)
        resultado, score = comparar_con_imagen(descriptors_cam, keypoints_cam, img_carpeta)
        if score < mejor_score:
            mejor_coincidencia = resultado
            mejor_score = score
            mejor_nombre = os.path.basename(img_path)

    # Mostrar el resultado
    if mejor_coincidencia is not None:
        mostrar_resultado(mejor_coincidencia, mejor_score, mejor_nombre)
    else:
        messagebox.showinfo("Información", "No se encontró una coincidencia válida.")


def mostrar_resultado(mejor_coincidencia, mejor_score, mejor_nombre):
    """ Muestra el resultado de la comparación en la interfaz. """
    im = Image.fromarray(mejor_coincidencia)
    img_to_show = ImageTk.PhotoImage(image=im)
    LImagenCarpeta.configure(image=img_to_show)
    LImagenCarpeta.image = img_to_show

    # Mostrar el nombre y puntaje
    CajaTexto2.configure(state='normal')
    CajaTexto2.delete(1.0, tk.END)
    CajaTexto2.insert(1.0, f"Imagen más similar: {mejor_nombre}\nScore: {mejor_score:.2f}")
    CajaTexto2.configure(state='disabled')


#Sliders para recorte de imagen
SX = tk.Scale(ventana, from_=0, to=300, orient='horizontal', command=actualizar_area_recorte)
SX.place(x=425,y=5, width=311)
SY = tk.Scale(ventana, from_=0, to=240, orient='vertical', command=actualizar_area_recorte)
SY.place(x=370,y=50, height=241)
SW = tk.Scale(ventana, from_=0, to=300, orient='horizontal', command=actualizar_area_recorte)
SW.place(x=425,y=295, width=311)
SW.set(300)
SH = tk.Scale(ventana, from_=0, to=240, orient='vertical', command=actualizar_area_recorte)
SH.place(x=730, y=50, height=241)
SH.set(240)

# Botones
BGuardar = tk.Button(ventana, text="Guardar Imagen", command=guardar_imagen)
BGuardar.place(x=900, y=310, width=120, height=23)
BCamara = tk.Button(ventana, text="Camara", command=camara)
BCamara.place(x=65, y=310, width=75, height=23)
BSeleccionarCarpeta = tk.Button(ventana, text="Seleccionar Carpeta", command=seleccionar_carpeta)
BSeleccionarCarpeta.place(x=120, y=350, width=120, height=23)
BCapturar = tk.Button(ventana, text="Iniciar captura", command=Capturar)
BFormas = tk.Button(ventana, text="Buscar Formas", command=rgb)
BFormas.place(x=580,y=360,width=131,height=23)
BCargarImagenes = tk.Button(ventana, text="Cargar Imágenes", command=cargar_imagenes_carpeta)
BCargarImagenes.place(x=1160, y=310, width=120, height=23)
BComparar = tk.Button(ventana, text="Comparar", command=comparar_imagenes)
BComparar.place(x=1340, y=310, width=100, height=23)
#BCompararCaptura = tk.Button(ventana, text="Comparar Captura", command=comparar_captura_con_carpeta)
#BCompararCaptura.place(x=580,y=380,width=131,height=23)


# Label
LUmbral = tk.Label(ventana, text="Umbralizacion")
LUmbral.place(x=420, y=353, width=125, height=16)

# Cuadros de Imagen
LImagen = tk.Label(ventana, background="gray")
LImagen.place(x=50,y=50,width=300,height=240)
LImagenUmbralizada = tk.Label(ventana, background="gray")
LImagenUmbralizada.place(x=50, y=400, width=300, height=240)
LImagen2 = tk.Label(ventana, background="gray")
LImagen2.place(x=430, y=50, width=300, height=240)
LImagenManchas = tk.Label(ventana, background="gray")
LImagenManchas.place(x=810,y=50,width=300,height=240)
LImagenCarpeta = tk.Label(ventana, bg="gray")
LImagenCarpeta.place(x=1150, y=50, width=300, height=240)

# Cuadro de Texto
CajaTexto = tk.Text(ventana, state="disabled")
CajaTexto.place(x=805,y=350,width=311,height=100)
CajaTexto2 = tk.Text(ventana, state="disabled")
CajaTexto2.place(x=1145,y=350,width=311,height=100)

# Spinbox
SGray = tk.Spinbox(ventana, from_=0, to=255)
SGray.place(x=460, y=380, width=45)

ventana.mainloop()