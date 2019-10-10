# BreakOut by EG
import time
import pygame

# Variables de la pantalla
ancho = 640
alto = 480
color = (24, 20, 37)
color_texto = (149, 233, 255)

# Cambiar icono
icono = pygame.image.load('img/icono.png')
pygame.display.set_icon(icono)

# Clases


class Escena:

    def __init__(self):
        "Inicializacion"
        self.proximaEscena = False
        self.jugando = True

    def leer_eventos(self, eventos):
        "Leer lista de eventos"
        pass

    def actualizar(self):
        "calculo y logica"
        pass

    def dibujar(self, pantalla):
        "Dibuja los objetos en pantalla"
        pass

    def cambiar_escena(self, escena):
        "Selecciona la nueva escena a ser desplegada"
        self.proximaEscena = escena


class Director:

    def __init__(self, titulo="", res=(ancho, alto)):
        # Inicializa todo lo importante
        pygame.init()

        # Creando la pantalla
        self.pantalla = pygame.display.set_mode(res)

        # Cambia el titulo de la ventana del juego
        pygame.display.set_caption(titulo)

        # Crear un reloj
        self.reloj = pygame.time.Clock()

        # Crea y maneja escenas
        self.escena = None
        self.escenas = {}

    def ejecutar(self, escena_inicial, fps=60):
        self.escena = self.escenas[escena_inicial]
        jugando = True

        while jugando:
            self.reloj.tick(fps)
            eventos = pygame.event.get()

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    jugando = False

            self.escena.leer_eventos(eventos)
            self.escena.actualizar()
            self.escena.dibujar(self.pantalla)

            self.elegirEscena(self.escena.proximaEscena)

            if jugando:
                jugando = self.escena.jugando

            pygame.display.update()

        time.sleep(3)

    def elegirEscena(self, proximaEscena):
        if proximaEscena:
            if proximaEscena not in self.escenas:
                self.agregarEscena(proximaEscena)

            self.escena = self.escenas[proximaEscena]

    def agregarEscena(self, escena):
        escenaClase = 'Escena' + escena
        escenaObj = globals()[escenaClase]

        self.escenas[escena] = escenaObj()


class EscenaNivel1(Escena):

    def __init__(self):
        Escena.__init__(self)

        # Creacion de los objetos
        self.Cant_Ladrillos = 70
        self.bolita = Bolita()
        self.jugador = Paleta()
        self.muro = Muro(self.Cant_Ladrillos)

        # Puntuacion y vida
        self.puntuacion = 0
        self.vidas = 3

        # Saque
        self.esperando_saque = True

        # Hace que se repitan los eventos de tecla presionada
        pygame.key.set_repeat(15)

    def leer_eventos(self, eventos):
        for evento in eventos:
            # Buscar eventos desde el teclado
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)

                # Hace que se pueda hacer un saque en el juego
                if self.esperando_saque is True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False

                    # Decida hacia que lado sale la bolita
                    if self.bolita.rect.centerx < (ancho / 2):
                        self.bolita.speed = [3, -3]

                    else:
                        self.bolita.speed = [-3, -3]

    def actualizar(self):
        # Actualizar la posicion de la bolita
        if self.esperando_saque is False:
            self.bolita.update()

        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop

        # Revisa si la bolita salio de la pantalla
        if self.bolita.rect.top > alto + 2:
            self.vidas -= 1
            self.esperando_saque = True

        # Revisa si las vidas se acabaron
        if self.vidas <= 0:
            self.cambiar_escena('JuegoTerminado')

        # Colision entre la bolita y el jugador
        if pygame.sprite.collide_rect(self.bolita, self.jugador):
            self.bolita.speed[1] = -self.bolita.speed[1]

        # Colision entre la bolita y los ladrillos
        self.lista = pygame.sprite.spritecollide(self.bolita, self.muro, False)

        if self.lista:
            self.ladrillo = self.lista[0]

            # Guarda la posicion de la bolita
            cx = self.bolita.rect.centerx

            # Detecta si fue golpeado el ladrillo por un lateral
            if cx < self.ladrillo.rect.left or cx > self.ladrillo.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]

            else:
                self.bolita.speed[1] = -self.bolita.speed[1]

            # Eliminamos el ladrillo y suma puntos
            self.muro.remove(self.ladrillo)
            self.puntuacion += 10
            self.Cant_Ladrillos -= 1
            if self.Cant_Ladrillos == 0:
                self.cambiar_escena('JuegoGanado')

    def dibujar(self, pantalla):
        # Cambia el color del fondo
        pantalla.fill(color)

        # Mostrar puntuacion
        self.mostrar_puntuacion(pantalla)

        # Mostrar vidas
        self.mostrar_vidas(pantalla)

        # Dibujar la bolita
        pantalla.blit(self.bolita.image, self.bolita.rect)

        # Dibujar la jugador
        pantalla.blit(self.jugador.image, self.jugador.rect)

        # Dibuja el muro
        self.muro.draw(pantalla)

    # Muestra la puntuacion
    def mostrar_puntuacion(self, pantalla):
        # Carga una fuente del sistema
        fuente = pygame.font.SysFont('Arial', 20)

        # Crea un texto con la fuente del sistema elegida
        texto = fuente.render(str(self.puntuacion).zfill(5), True, color_texto)

        # Obtiene el rect y lo posciciona en la pantalla
        texto_rect = texto.get_rect()
        texto_rect.topleft = (10, 10)

        # Lo dibuja en la pantalla
        pantalla.blit(texto, texto_rect)

    # Muestra las vidas
    def mostrar_vidas(self, pantalla):
        # Carga una fuente del sistema
        fuente = pygame.font.SysFont('Arial', 20)

        cadena = 'Vidas: ' + str(self.vidas - 1).zfill(2)

        # Crea un texto con la fuente del sistema elegida
        texto = fuente.render(cadena, True, color_texto)

        # Obtiene el rect y lo posciciona en la pantalla
        texto_rect = texto.get_rect()
        texto_rect.topright = (ancho - 10, 10)

        # Lo dibuja en la pantalla
        pantalla.blit(texto, texto_rect)


class EscenaJuegoTerminado(Escena):

    def actualizar(self):
        self.jugando = False

    def dibujar(self, pantalla):
        # Carga una fuente del sistema
        fuente = pygame.font.SysFont('Arial', 62)

        # Crea un texto con la fuente del sistema elegida
        texto = fuente.render("Juego Terminado :'v", True, color_texto)

        # Obtiene el rect y lo posciciona en la pantalla
        texto_rect = texto.get_rect()
        texto_rect.center = (ancho / 2, alto / 2)

        # Cambia el color del fondo
        pantalla.fill(color)

        # Lo dibuja en la pantalla
        pantalla.blit(texto, texto_rect)

        # Actualiza toda la pantalla
        pygame.display.flip()


class EscenaJuegoGanado(Escena):

    def actualizar(self):
        self.jugando = False

    def dibujar(self, pantalla):
        # Carga una fuente del sistema
        fuente = pygame.font.SysFont('Arial', 62)

        # Crea un texto con la fuente del sistema elegida
        texto = fuente.render("Nivel completado", True, color_texto)

        # Obtiene el rect y lo posciciona en la pantalla
        texto_rect = texto.get_rect()
        texto_rect.center = (ancho / 2, alto / 2)

        # Cambia el color del fondo
        pantalla.fill(color)

        # Lo dibuja en la pantalla
        pantalla.blit(texto, texto_rect)

        # Actualiza toda la pantalla
        pygame.display.flip()


class Bolita(pygame.sprite.Sprite):

    def __init__(self):
        # Inicializa el constructor de la clase
        pygame.sprite.Sprite.__init__(self)

        # Cargar imagen
        self.image = pygame.image.load('img/bolita.png')

        # Obtener el rectangulo de la imagen
        self.rect = self.image.get_rect()

        # Posicion inicial
        self.rect.center = (ancho / 2, alto / 2)

        # Velocidad inicial
        self.speed = [3, 3]

    def update(self):
        # Evita que se salga la bolita por arriba y abajo
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]

        # Evita que se salga la bolita por los lados
        if self.rect.right >= ancho or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]

        # Cambia la velocidad y direccion de la bolita
        self.rect.move_ip(self.speed)


class Paleta(pygame.sprite.Sprite):

    def __init__(self):
        # Inicializa el constructor de la clase
        pygame.sprite.Sprite.__init__(self)

        # Cargar imagen
        self.image = pygame.image.load('img/paleta.png')

        # Obtener el rectangulo de la imagen
        self.rect = self.image.get_rect()

        # Posicion inicial
        self.rect.midbottom = (ancho / 2, alto - 20)

        # Velocidad inicial
        self.speed = [0, 0]

    def update(self, evento):
        # Busca si se preciono la tecla izquierda
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-5, 0]

        # Busca si se preciono la tecla derecha
        elif evento.key == pygame.K_RIGHT and self.rect.right < ancho:
            self.speed = [5, 0]

        # Detiene la paleta
        else:
            self.speed = [0, 0]

        # Cambia la velocidad de la paleta
        self.rect.move_ip(self.speed)


class Ladrillo(pygame.sprite.Sprite):

    def __init__(self, posicion):
        # Inicializa el constructor de la clase
        pygame.sprite.Sprite.__init__(self)

        # Cargar imagen
        self.image = pygame.image.load('img/ladrillo.png')

        # Obtener el rectangulo de la imagen
        self.rect = self.image.get_rect()

        # Posicion inicial, provista externamente
        self.rect.topleft = posicion


class Muro(pygame.sprite.Group):

    def __init__(self, cantidadLadrillos):
        # Inicializa el constructor de la clase
        pygame.sprite.Group.__init__(self)

        # Variables de posicion de los ladrillos
        pos_x = 40
        pos_y = 60

        # Bucle para la creacion de ladrillos
        for x in range(cantidadLadrillos):

            # Creamos los ladrillos y los agregamos
            ladrillo = Ladrillo((pos_x, pos_y))

            self.add(ladrillo)

            # Cambiamos la posicion del ladrillo
            pos_x += ladrillo.rect.width

            if pos_x >= ancho - 40:
                pos_x = 40
                pos_y += ladrillo.rect.height + 1


director = Director('BreakOut (Olivia)', (ancho, alto))
director.agregarEscena('Nivel1')
director.ejecutar('Nivel1')
