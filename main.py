import os
import pygame
import random
import math
import time
import threading
import json

# Obtener la ruta base donde se encuentra el archivo main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    """Devuelve la ruta completa de un archivo dentro de la misma carpeta que main.py."""
    return os.path.join(BASE_DIR, filename)

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Cargar una imagen personalizada
icono_personalizado = pygame.image.load(get_path("big_logo.png"))
pygame.display.set_icon(icono_personalizado)

# Cargar la imagen de la textura para los bloques
imagen_bloque = pygame.image.load(get_path("textura_bloque.png"))

# Escalar la imagen de la textura para los bloques al tamaño deseado
tamaño_bloque = 53  # Cambia este valor para aumentar el tamaño de los bloques
imagen_bloque_redimensionada = pygame.transform.scale(imagen_bloque, (tamaño_bloque, tamaño_bloque))

# Configuraciones básicas
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption("Subliminal")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (0, 100, 0)
ROJO = (255, 0, 0)

# Velocidades
VEL_JUGADOR_MAX = 10

# Reloj
FPS = 60
clock = pygame.time.Clock()

# Jugador
jugador_radio = 15
jugador_hitbox_radio = 10  # Radio de la hitbox para el jugador
jugador_pos = [ANCHO // 2, ALTO // 2]
jugador_img_original = pygame.image.load(get_path("jugador.png"))  # Imagen del jugador
jugador_rotacion = 0

balas = []
cooldown_balas = 300  # 300ms cooldown entre disparos
ultimo_disparo = pygame.time.get_ticks()

# Fondo y mapa (aumentado)
mapa_ancho, mapa_alto = 6400, 4800  # Tamaño del mapa ampliado
fondo_pos = [-(mapa_ancho - ANCHO) // 2, -(mapa_alto - ALTO) // 2]

# Enemigos
enemigos = []
max_enemigos = 10
distancia_minima_enemigo = 400  # Distancia mínima para que aparezca un enemigo
distancia_maxima_enemigo = 800  # Distancia máxima para que aparezca un enemigo
enemigo_hitbox_radio = 30  # Radio de la hitbox para los enemigos
enemigo_img_original = pygame.image.load(get_path("enemigo.png"))  # Imagen de los enemigos

# Nuevas criaturas (enemigos que disparan)
criaturas_disparadoras = []
max_criaturas_disparadoras = 3
criatura_disparadora_img_original = pygame.image.load(get_path("criatura_disparadora.png"))  # Imagen de la criatura que dispara
criatura_disparadora_hitbox_radio = 40  # Radio de la hitbox para la criatura que dispara
cooldown_disparo_criatura = 1000  # Tiempo de cooldown entre disparos de la criatura
ultimo_disparo_criatura = pygame.time.get_ticks()
balas_criaturas = []  # Balas disparadas por las criaturas

# Bloques
bloques = []
tamaño_bloque = 40

# Contador de masa verde
green_mass = 0

# Modos de juego
modo_aventura = True  # True para modo aventura, False para modo construcción

# Vida del jugador
vida_maxima = 10
vida_jugador = vida_maxima
daño_base = 0.01  # Daño base por enemigo que te toca
regeneracion_vida = 0.01  # Velocidad de regeneración de vida

# Fuente para las coordenadas, el contador de masa verde, el modo y la vida (tamaño reducido)
fuente_pequena = pygame.font.Font(None, 24)

# Función para ajustar la orientación inicial de la imagen del jugador
def ajustar_orientacion_inicial(angulo_inicial):
    global jugador_img_original
    jugador_img_rotada = pygame.transform.rotate(jugador_img_original, angulo_inicial)
    return jugador_img_rotada

# Función para ajustar el tamaño de la imagen
def ajustar_tamaño_imagen(imagen, nuevo_ancho, nuevo_alto):
    return pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))

# Configura la orientación inicial del jugador (en grados)
angulo_inicial_jugador = 135  # Cambia esto según la orientación que prefieras
jugador_img = ajustar_orientacion_inicial(angulo_inicial_jugador)

# Configura el tamaño de las imágenes
tamaño_jugador = (jugador_radio * 4, jugador_radio * 4)  # Cambia el tamaño según lo que necesites
tamaño_enemigo = (60, 60)  # Cambia el tamaño de los enemigos
tamaño_criatura_disparadora = (50, 50)  # Tamaño de la criatura que dispara

jugador_img = ajustar_tamaño_imagen(jugador_img, *tamaño_jugador)
enemigo_img = ajustar_tamaño_imagen(enemigo_img_original, *tamaño_enemigo)
criatura_disparadora_img = ajustar_tamaño_imagen(criatura_disparadora_img_original, *tamaño_criatura_disparadora)

def generar_fondo_con_estrellas():
    estrellas = []
    num_estrellas = 500  # Aumenta el número de estrellas proporcionalmente al tamaño del mapa
    for _ in range(num_estrellas):
        x = random.randint(0, mapa_ancho)
        y = random.randint(0, mapa_alto)
        tamaño = random.randint(1, 3)
        brillo = random.randint(100, 255)
        estrellas.append({'pos': (x, y), 'tamaño': tamaño, 'brillo': (brillo, brillo, brillo)})
    return estrellas

estrellas_fondo = generar_fondo_con_estrellas()

# Función para dibujar
def dibujar_ventana():
    VENTANA.fill(NEGRO)

    # Dibujar estrellas del fondo
    for estrella in estrellas_fondo:
        pygame.draw.circle(VENTANA, estrella['brillo'], (estrella['pos'][0] + fondo_pos[0], estrella['pos'][1] + fondo_pos[1]), estrella['tamaño'])

    # Dibujar bloques con la imagen redimensionada
    for bloque in bloques:
        VENTANA.blit(imagen_bloque_redimensionada, bloque.move(fondo_pos[0], fondo_pos[1]))

    # Dibujar el resto del contenido como enemigos, balas, jugador, etc.
    # (El resto del código permanece igual)

    # Dibujar enemigos
    for enemigo in enemigos:
        enemigo_img_rotada = pygame.transform.rotate(enemigo_img, enemigo['rotacion'])
        enemigo_pos = (enemigo['pos'][0] + fondo_pos[0] - enemigo_img_rotada.get_width() // 2, 
                       enemigo['pos'][1] + fondo_pos[1] - enemigo_img_rotada.get_height() // 2)
        VENTANA.blit(enemigo_img_rotada, enemigo_pos)

    # Dibujar criaturas que disparan
    for criatura in criaturas_disparadoras:
        criatura_img_rotada = pygame.transform.rotate(criatura_disparadora_img, criatura['rotacion'])
        criatura_pos = (criatura['pos'][0] + fondo_pos[0] - criatura_img_rotada.get_width() // 2, 
                        criatura['pos'][1] + fondo_pos[1] - criatura_img_rotada.get_height() // 2)
        VENTANA.blit(criatura_img_rotada, criatura_pos)

    # Dibujar balas
    for bala in balas:
        pygame.draw.circle(VENTANA, BLANCO, [bala['pos'][0] + fondo_pos[0], bala['pos'][1] + fondo_pos[1]], 5)
    for bala in balas_criaturas:
        pygame.draw.circle(VENTANA, ROJO, [bala['pos'][0] + fondo_pos[0], bala['pos'][1] + fondo_pos[1]], 5)

    # Dibujar jugador (siempre en el centro)
    jugador_img_rotada = pygame.transform.rotate(jugador_img, jugador_rotacion)
    jugador_pos_img = (jugador_pos[0] - jugador_img_rotada.get_width() // 2, jugador_pos[1] - jugador_img_rotada.get_height() // 2)
    VENTANA.blit(jugador_img_rotada, jugador_pos_img)

    # Mostrar coordenadas, modo, contador de masa verde y vida
    coord_x = int(jugador_pos[0] - fondo_pos[0])
    coord_y = int(jugador_pos[1] - fondo_pos[1])
    coordenadas_texto = fuente_pequena.render(f"Coordinates: ({coord_x}, {coord_y})", True, BLANCO)
    modo_texto = fuente_pequena.render("Mode: Construction" if not modo_aventura else "Mode: Adventure", True, ROJO)
    green_mass_texto = fuente_pequena.render(f"Space Debris: {green_mass}", True, BLANCO)
    vida_texto = fuente_pequena.render(f"Life {int(vida_jugador)}/{vida_maxima}", True, BLANCO)

    VENTANA.blit(coordenadas_texto, (10, 10))
    VENTANA.blit(modo_texto, (10, 30))
    VENTANA.blit(green_mass_texto, (10, 50))
    VENTANA.blit(vida_texto, (10, 70))

    # Añadir una tonalidad roja según la cantidad de vida perdida
    if vida_jugador < vida_maxima:
        intensidad_roja = int((1 - vida_jugador / vida_maxima) * 255)
        overlay = pygame.Surface((ANCHO, ALTO))
        overlay.set_alpha(intensidad_roja)
        overlay.fill(ROJO)
        VENTANA.blit(overlay, (0, 0))

    pygame.display.update()

# Función para detectar colisiones con bloques
def detectar_colision(objeto_rect, lista_bloques):
    for bloque in lista_bloques:
        if objeto_rect.colliderect(bloque):
            return True
    return False

# Función para alinear las coordenadas al centro del bloque más cercano
def alinear_a_centro(coordenada, tamaño):
    return (coordenada // tamaño) * tamaño + tamaño // 2

# Función para calcular el ángulo de rotación hacia un punto
def calcular_rotacion(origen, destino):
    dx = destino[0] - origen[0]
    dy = destino[1] - origen[1]
    return math.degrees(math.atan2(-dy, dx))

# Función para reproducir música de fondo
def reproducir_musica():
    lista_canciones = [get_path("Carmina_Burana.mp3"), get_path("Dies_Irae.mp3"), get_path("strauss.mp3"), get_path("The_Planets.mp3"), get_path("Vallkyres.mp3")]
    volumen_musica = 0.3  # Ajusta este valor entre 0.0 y 1.0 según el volumen que prefieras
    while True:
        cancion = random.choice(lista_canciones)
        pygame.mixer.music.load(get_path(cancion))
        pygame.mixer.music.set_volume(volumen_musica)  # Establecer el volumen de la música
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(100)
        pygame.time.delay(random.randint(5000, 10000))  # Esperar entre 5 y 10 segundos antes de reproducir otra canción

# Iniciar la reproducción de música en un hilo separado para no bloquear el juego
hilo_musica = threading.Thread(target=reproducir_musica, daemon=True)
hilo_musica.start()

# Funciones para reproducir efectos de sonido
def reproducir_sonido_disparo():
    sonido_disparo = pygame.mixer.Sound(get_path("Piuuu.mp3"))
    sonido_disparo.play()

def reproducir_sonido_explosion():
    sonido_explosion = pygame.mixer.Sound(get_path("Bammm.mp3"))
    sonido_explosion.play()

# Función para guardar el progreso del juego
def guardar_progreso():
    progreso = {
        "bloques": [{"x": bloque.x, "y": bloque.y, "width": bloque.width, "height": bloque.height} for bloque in bloques],
        "green_mass": green_mass,
        "jugador_pos": jugador_pos,
        "vida_jugador": vida_jugador,
        "fondo_pos": fondo_pos
    }
    with open("world.json", "w") as archivo_guardado:
        json.dump(progreso, archivo_guardado)

# Función para cargar el progreso del juego
def cargar_progreso():
    global bloques, green_mass, jugador_pos, vida_jugador, fondo_pos
    try:
        with open("world.json", "r") as archivo_guardado:
            progreso = json.load(archivo_guardado)
            bloques = [pygame.Rect(b["x"], b["y"], b["width"], b["height"]) for b in progreso["bloques"]]
            green_mass = progreso["green_mass"]
            jugador_pos = progreso["jugador_pos"]
            vida_jugador = progreso["vida_jugador"]
            fondo_pos = progreso["fondo_pos"]
    except FileNotFoundError:
        print("No se encontró un archivo de guardado. Iniciando nuevo juego.")

# Cargar el progreso al inicio del juego
cargar_progreso()

# Bucle principal del juego
corriendo = True
while corriendo:
    clock.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            guardar_progreso()
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                guardar_progreso()
                corriendo = False
            if evento.key == pygame.K_v:  # Cambiar de modo
                modo_aventura = not modo_aventura
        if evento.type == pygame.VIDEORESIZE:  # Manejar el redimensionamiento de la ventana
            ANCHO, ALTO = evento.w, evento.h
            VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
            jugador_pos = [ANCHO // 2, ALTO // 2]
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Botón izquierdo del ratón
                if modo_aventura:  # En modo aventura, disparar
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - ultimo_disparo >= cooldown_balas:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        dx = mouse_x - jugador_pos[0]
                        dy = mouse_y - jugador_pos[1]
                        magnitud = (dx**2 + dy**2) ** 0.5
                        if magnitud != 0:
                            dx /= magnitud
                            dy /= magnitud
                        # Aumentar la velocidad de las balas
                        velocidad_bala = 20  # Ajusta este valor para cambiar la velocidad
                        balas.append({'pos': [jugador_pos[0] - fondo_pos[0], jugador_pos[1] - fondo_pos[1]], 'dir': [dx * velocidad_bala, dy * velocidad_bala]})

                        ultimo_disparo = tiempo_actual
                        reproducir_sonido_disparo()  # Reproducir sonido de disparo
                else:  # En modo construcción, colocar bloque
                    if green_mass >= 2:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        bloque_x = alinear_a_centro(jugador_pos[0] - fondo_pos[0] + (mouse_x - ANCHO//2), tamaño_bloque)
                        bloque_y = alinear_a_centro(jugador_pos[1] - fondo_pos[1] + (mouse_y - ALTO//2), tamaño_bloque)
                        nuevo_bloque = pygame.Rect(bloque_x - tamaño_bloque // 2, bloque_y - tamaño_bloque // 2, tamaño_bloque, tamaño_bloque)
                        
                        # Verificar si el bloque no colisiona con otros bloques antes de crearlo
                        if not detectar_colision(nuevo_bloque, bloques):
                            bloques.append(nuevo_bloque)
                            green_mass -= 2
            if evento.button == 3:
                if modo_aventura:
                    VEL_JUGADOR_MAX = 15  # Cambiar la velocidad del jugador a 15
        if evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 3:
                VEL_JUGADOR_MAX = 10  # Restaurar la velocidad del jugador a su valor original

    if modo_aventura:
        # Movimiento del fondo basado en la posición del ratón
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - jugador_pos[0]
        dy = mouse_y - jugador_pos[1]
        distancia = (dx**2 + dy**2) ** 0.5

        if distancia > 0:
            factor_velocidad = min(distancia / 100, 1)  # Controlar la velocidad según la distancia
            nuevo_fondo_x = fondo_pos[0] - dx / distancia * VEL_JUGADOR_MAX * factor_velocidad
            nuevo_fondo_y = fondo_pos[1] - dy / distancia * VEL_JUGADOR_MAX * factor_velocidad

            # Crear un rectángulo temporal para verificar colisiones y límites del mapa
            jugador_rect = pygame.Rect(jugador_pos[0] - jugador_hitbox_radio, jugador_pos[1] - jugador_hitbox_radio, jugador_hitbox_radio * 2, jugador_hitbox_radio * 2)
            jugador_rect.move_ip(-nuevo_fondo_x, -nuevo_fondo_y)

            if not detectar_colision(jugador_rect, bloques):
                # Asegurarse de que el jugador no se mueva fuera de los límites del mapa
                if -(mapa_ancho - ANCHO) <= nuevo_fondo_x <= 0:
                    fondo_pos[0] = nuevo_fondo_x
                if -(mapa_alto - ALTO) <= nuevo_fondo_y <= 0:
                    fondo_pos[1] = nuevo_fondo_y

        # Calcular la rotación del jugador hacia el ratón
        jugador_rotacion = calcular_rotacion(jugador_pos, (mouse_x, mouse_y))
    else:
        # Movimiento del jugador en modo construcción con teclas WASD
        keys = pygame.key.get_pressed()

        # Propuesta de nuevo movimiento
        nuevo_fondo_x, nuevo_fondo_y = fondo_pos[0], fondo_pos[1]

        if keys[pygame.K_w]:
            nuevo_fondo_y += VEL_JUGADOR_MAX
        if keys[pygame.K_s]:
            nuevo_fondo_y -= VEL_JUGADOR_MAX
        if keys[pygame.K_a]:
            nuevo_fondo_x += VEL_JUGADOR_MAX
        if keys[pygame.K_d]:
            nuevo_fondo_x -= VEL_JUGADOR_MAX

        # Crear un rectángulo temporal para el jugador en la nueva posición propuesta
        jugador_rect = pygame.Rect(jugador_pos[0] - jugador_hitbox_radio, jugador_pos[1] - jugador_hitbox_radio, jugador_hitbox_radio * 2, jugador_hitbox_radio * 2)
        jugador_rect.move_ip(-nuevo_fondo_x, -nuevo_fondo_y)

        # Verificar colisiones y límites del mapa
        if not detectar_colision(jugador_rect, bloques):
            if -(mapa_ancho - ANCHO) <= nuevo_fondo_x <= 0:
                fondo_pos[0] = nuevo_fondo_x
            if -(mapa_alto - ALTO) <= nuevo_fondo_y <= 0:
                fondo_pos[1] = nuevo_fondo_y

    # Movimiento de las balas del jugador
    for bala in balas[:]:
        bala['pos'][0] += bala['dir'][0]
        bala['pos'][1] += bala['dir'][1]
        bala_rect = pygame.Rect(bala['pos'][0], bala['pos'][1], 5, 5)

        # Verificar colisión con bloques
        if detectar_colision(bala_rect, bloques):
            for bloque in bloques:
                if bala_rect.colliderect(bloque):
                    bloques.remove(bloque)
                    balas.remove(bala)
                    green_mass += 1
                    break

    # Movimiento de las balas de las criaturas
    for bala in balas_criaturas[:]:
        bala['pos'][0] += bala['dir'][0]
        bala['pos'][1] += bala['dir'][1]
        bala_rect = pygame.Rect(bala['pos'][0], bala['pos'][1], 5, 5)

        # Verificar colisión con bloques
        if detectar_colision(bala_rect, bloques):
            balas_criaturas.remove(bala)
            continue

        # Verificar colisión con el jugador
        if bala_rect.colliderect(jugador_rect):
            vida_jugador -= 1
            balas_criaturas.remove(bala)
            continue

        # Eliminar balas fuera del mapa
        if not (0 < bala['pos'][0] < mapa_ancho and 0 < bala['pos'][1] < mapa_alto):
            balas_criaturas.remove(bala)


    # Comprobar colisiones entre balas y enemigos
    for bala in balas[:]:
        # Colisión con enemigos normales
        for enemigo in enemigos[:]:
            dist_bala_enemigo = ((bala['pos'][0] - enemigo['pos'][0])**2 + (bala['pos'][1] - enemigo['pos'][1])**2) ** 0.5
            if dist_bala_enemigo < enemigo_hitbox_radio + 5:  # 5 es el radio de la bala
                if bala in balas:  # Verificar si la bala aún está en la lista
                    balas.remove(bala)
                if enemigo in enemigos:  # Verificar si el enemigo aún está en la lista
                    enemigos.remove(enemigo)
                    reproducir_sonido_explosion()  # Reproducir sonido de explosión
                green_mass += 1

        # Colisión con criaturas disparadoras
        for criatura in criaturas_disparadoras[:]:
            dist_bala_criatura = ((bala['pos'][0] - criatura['pos'][0])**2 + (bala['pos'][1] - criatura['pos'][1])**2) ** 0.5
            if dist_bala_criatura < criatura_disparadora_hitbox_radio + 5:  # 5 es el radio de la bala
                if bala in balas:  # Verificar si la bala aún está en la lista
                    balas.remove(bala)
                if criatura in criaturas_disparadoras:  # Verificar si la criatura aún está en la lista
                    criaturas_disparadoras.remove(criatura)
                    reproducir_sonido_explosion()  # Reproducir sonido de explosión
                green_mass += 1


    # Generar y mover enemigos
    if len(enemigos) < max_enemigos:
        enemigo_radio = random.randint(10, 20)

        enemigo_x_min = int(max(jugador_pos[0] - fondo_pos[0] + distancia_minima_enemigo, 0))
        enemigo_x_max = int(min(mapa_ancho, jugador_pos[0] - fondo_pos[0] + distancia_maxima_enemigo))
        if enemigo_x_min > enemigo_x_max:
            enemigo_x_min, enemigo_x_max = enemigo_x_max, enemigo_x_min

        enemigo_y_min = int(max(jugador_pos[1] - fondo_pos[1] + distancia_minima_enemigo, 0))
        enemigo_y_max = int(min(mapa_alto, jugador_pos[1] - fondo_pos[1] + distancia_maxima_enemigo))
        if enemigo_y_min > enemigo_y_max:
            enemigo_y_min, enemigo_y_max = enemigo_y_max, enemigo_y_min

        enemigo_x = random.randint(enemigo_x_min, enemigo_x_max)
        enemigo_y = random.randint(enemigo_y_min, enemigo_y_max)
        nuevo_enemigo = {'pos': [enemigo_x, enemigo_y], 'radio': enemigo_radio, 'rotacion': 0}
        
        # Evitar que los enemigos aparezcan dentro de bloques
        enemigo_rect = pygame.Rect(enemigo_x - enemigo_hitbox_radio, enemigo_y - enemigo_hitbox_radio, enemigo_hitbox_radio * 2, enemigo_hitbox_radio * 2)
        if not detectar_colision(enemigo_rect, bloques):
            enemigos.append(nuevo_enemigo)

    for enemigo in enemigos:
        # Movimiento propuesto para el enemigo
        dx, dy = 0, 0
        if enemigo['pos'][0] < jugador_pos[0] - fondo_pos[0]:
            dx = 1
        if enemigo['pos'][0] > jugador_pos[0] - fondo_pos[0]:
            dx = -1
        if enemigo['pos'][1] < jugador_pos[1] - fondo_pos[1]:
            dy = 1
        if enemigo['pos'][1] > jugador_pos[1] - fondo_pos[1]:
            dy = -1

        # Crear un rectángulo temporal para el enemigo en la nueva posición propuesta
        enemigo_rect = pygame.Rect(enemigo['pos'][0] - enemigo_hitbox_radio, enemigo['pos'][1] - enemigo_hitbox_radio, enemigo_hitbox_radio * 2, enemigo_hitbox_radio * 2)
        enemigo_rect.move_ip(dx, dy)

        # Verificar colisión con bloques antes de mover al enemigo
        if not detectar_colision(enemigo_rect, bloques):
            enemigo['pos'][0] += dx
            enemigo['pos'][1] += dy

        # Calcular la rotación del enemigo hacia el jugador
        enemigo['rotacion'] = calcular_rotacion(enemigo['pos'], (jugador_pos[0] - fondo_pos[0], jugador_pos[1] - fondo_pos[1]))

        # Comprobar colisión con el jugador
        dist_jugador_enemigo = ((enemigo['pos'][0] - (jugador_pos[0] - fondo_pos[0]))**2 + (enemigo['pos'][1] - (jugador_pos[1] - fondo_pos[1]))**2) ** 0.5
        if dist_jugador_enemigo < enemigo_hitbox_radio + jugador_hitbox_radio:
            # Restar vida proporcional al número de enemigos que te tocan
            vida_jugador -= daño_base * len(enemigos)

    # Generar y mover criaturas que disparan
    if len(criaturas_disparadoras) < max_criaturas_disparadoras:
        criatura_radio = random.randint(20, 30)

        criatura_x_min = int(max(jugador_pos[0] - fondo_pos[0] + distancia_minima_enemigo, 0))
        criatura_x_max = int(min(mapa_ancho, jugador_pos[0] - fondo_pos[0] + distancia_maxima_enemigo))
        if criatura_x_min > criatura_x_max:
            criatura_x_min, criatura_x_max = criatura_x_max, criatura_x_min

        criatura_y_min = int(max(jugador_pos[1] - fondo_pos[1] + distancia_minima_enemigo, 0))
        criatura_y_max = int(min(mapa_alto, jugador_pos[1] - fondo_pos[1] + distancia_maxima_enemigo))
        if criatura_y_min > criatura_y_max:
            criatura_y_min, criatura_y_max = criatura_y_max, criatura_y_min

        criatura_x = random.randint(criatura_x_min, criatura_x_max)
        criatura_y = random.randint(criatura_y_min, criatura_y_max)
        nueva_criatura = {'pos': [criatura_x, criatura_y], 'radio': criatura_radio, 'rotacion': 0}
        
        # Evitar que las criaturas aparezcan dentro de bloques
        criatura_rect = pygame.Rect(criatura_x - criatura_disparadora_hitbox_radio, criatura_y - criatura_disparadora_hitbox_radio, criatura_disparadora_hitbox_radio * 2, criatura_disparadora_hitbox_radio * 2)
        if not detectar_colision(criatura_rect, bloques):
            criaturas_disparadoras.append(nueva_criatura)

    for criatura in criaturas_disparadoras:
        # Movimiento propuesto para la criatura
        dx, dy = 0, 0
        if criatura['pos'][0] < jugador_pos[0] - fondo_pos[0]:
            dx = 1
        if criatura['pos'][0] > jugador_pos[0] - fondo_pos[0]:
            dx = -1
        if criatura['pos'][1] < jugador_pos[1] - fondo_pos[1]:
            dy = 1
        if criatura['pos'][1] > jugador_pos[1] - fondo_pos[1]:
            dy = -1

        # Crear un rectángulo temporal para la criatura en la nueva posición propuesta
        criatura_rect = pygame.Rect(criatura['pos'][0] - criatura_disparadora_hitbox_radio, criatura['pos'][1] - criatura_disparadora_hitbox_radio, criatura_disparadora_hitbox_radio * 2, criatura_disparadora_hitbox_radio * 2)
        criatura_rect.move_ip(dx, dy)

        # Verificar colisión con bloques antes de mover a la criatura
        if not detectar_colision(criatura_rect, bloques):
            criatura['pos'][0] += dx
            criatura['pos'][1] += dy

        # Calcular la rotación de la criatura hacia el jugador
        criatura['rotacion'] = calcular_rotacion(criatura['pos'], (jugador_pos[0] - fondo_pos[0], jugador_pos[1] - fondo_pos[1]))

        # Comprobar colisión con el jugador
        dist_jugador_criatura = ((criatura['pos'][0] - (jugador_pos[0] - fondo_pos[0]))**2 + (criatura['pos'][1] - (jugador_pos[1] - fondo_pos[1]))**2) ** 0.5
        if dist_jugador_criatura < criatura_disparadora_hitbox_radio + jugador_hitbox_radio:
            # Restar vida al jugador si lo toca
            vida_jugador -= 1

        # La criatura dispara al jugador
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - ultimo_disparo_criatura >= cooldown_disparo_criatura:
            dx = jugador_pos[0] - fondo_pos[0] - criatura['pos'][0]
            dy = jugador_pos[1] - fondo_pos[1] - criatura['pos'][1]
            magnitud = (dx**2 + dy**2) ** 0.5
            if magnitud != 0:
                dx /= magnitud
                dy /= magnitud
            balas_criaturas.append({'pos': [criatura['pos'][0], criatura['pos'][1]], 'dir': [dx * 5, dy * 5]})
            ultimo_disparo_criatura = tiempo_actual

    # Limitar la vida del jugador a un máximo y un mínimo de 0
    if vida_jugador < 0:
        vida_jugador = 0
    elif vida_jugador < vida_maxima:
        vida_jugador += regeneracion_vida  # Regenerar vida lentamente

    # Dibujar todo
    dibujar_ventana()

pygame.quit()
