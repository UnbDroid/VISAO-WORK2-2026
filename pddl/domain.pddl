(define (domain robocup-work-transport)

  (:requirements :strips :typing)

  (:types
    robot
    location   ; workstations (WS_x), prateleiras (SH_x), mesa de precisão (PP), etc.
    object     ; ATTCs e objetos ADVANCED (AprilTags)
    container  ; caixas plásticas (ex: container azul/vermelho)
    slot       ; unidades de capacidade de carga do robô (máx. 3, por regra)
  )

  (:predicates
    (at-robot ?r - robot ?l - location)
    (obj-at ?o - object ?l - location)                 ; objeto solto em uma localização
    (container-at ?c - container ?l - location)        ; container fixo em uma localização
    (in-container ?o - object ?c - container)           ; objeto dentro de um container
    (holding ?r - robot ?o - object)                    ; robô segurando o objeto
    (holding-in ?r - robot ?o - object ?s - slot)        ; vincula objeto ao slot de carga usado
    (slot-free ?r - robot ?s - slot)                     ; slot de carga disponível
  )

  ;; Move o robô entre duas localizações (grafo totalmente conectado nesta versão)
  (:action move
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (at-robot ?r ?from)
    :effect (and (not (at-robot ?r ?from)) (at-robot ?r ?to))
  )

  ;; Pega um objeto que está solto em uma localização (mesa, prateleira, etc.)
  (:action pick-from-location
    :parameters (?r - robot ?o - object ?l - location ?s - slot)
    :precondition (and (at-robot ?r ?l) (obj-at ?o ?l) (slot-free ?r ?s))
    :effect (and
      (not (obj-at ?o ?l))
      (holding ?r ?o)
      (not (slot-free ?r ?s))
      (holding-in ?r ?o ?s))
  )

  ;; Pega um objeto que está dentro de um container
  (:action pick-from-container
    :parameters (?r - robot ?o - object ?c - container ?l - location ?s - slot)
    :precondition (and
      (at-robot ?r ?l)
      (container-at ?c ?l)
      (in-container ?o ?c)
      (slot-free ?r ?s))
    :effect (and
      (not (in-container ?o ?c))
      (holding ?r ?o)
      (not (slot-free ?r ?s))
      (holding-in ?r ?o ?s))
  )

  ;; Solta um objeto em uma localização (mesa, prateleira, mesa de precisão, etc.)
  (:action place-at-location
    :parameters (?r - robot ?o - object ?l - location ?s - slot)
    :precondition (and (at-robot ?r ?l) (holding ?r ?o) (holding-in ?r ?o ?s))
    :effect (and
      (not (holding ?r ?o))
      (not (holding-in ?r ?o ?s))
      (slot-free ?r ?s)
      (obj-at ?o ?l))
  )

  ;; Coloca um objeto dentro de um container presente na localização atual
  (:action place-in-container
    :parameters (?r - robot ?o - object ?c - container ?l - location ?s - slot)
    :precondition (and
      (at-robot ?r ?l)
      (container-at ?c ?l)
      (holding ?r ?o)
      (holding-in ?r ?o ?s))
    :effect (and
      (not (holding ?r ?o))
      (not (holding-in ?r ?o ?s))
      (slot-free ?r ?s)
      (in-container ?o ?c))
  )
)
