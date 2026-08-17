(define (problem bmt-instance) (:domain robocup-work-transport)
(:objects
    robot1 - robot

    start ws1 ws8 - location

    s1 s2 s3 - slot

    cont10 cont16 - container

    obj1 obj2 obj4 obj7 - object
)

(:init
    (at-robot robot1 start)
    (slot-free robot1 s1)
    (slot-free robot1 s2)
    (slot-free robot1 s3)

    (container-at cont10 ws8)   ; container azul
    (container-at cont16 ws8)   ; container vermelho

    (obj-at obj1 ws1)
    (obj-at obj2 ws1)
    (obj-at obj4 ws1)
    (obj-at obj7 ws1)
)

(:goal (and
    (in-container obj2 cont10)
    (in-container obj4 cont10)

    (in-container obj1 cont16)
    (in-container obj7 cont16)
))


)
