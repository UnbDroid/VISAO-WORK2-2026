(define (problem att1-instance) (:domain robocup-work-transport)
(:objects 
    robot1 - robot

    start ws1 ws3 ws4 ws6 ws8 sh2 - location

    s1 s2 s3 - slot

    obj20 obj21 obj22 obj23 obj24 obj25 obj12 obj15 obj16 - object
)

(:init
    (at-robot robot1 start)
    (slot-free robot1 s1)
    (slot-free robot1 s2)
    (slot-free robot1 s3)

    (obj-at obj12 ws1)
    (obj-at obj20 ws1)
    (obj-at obj22 ws1)

    (obj-at obj15 ws3)

    (obj-at obj21 sw4)
    (obj-at obj23 sw4)
    (obj-at obj24 sw4)

    (obj-at obj16 ws6)
    (obj-at obj25 ws6)
)

(:goal (and
    (obj-at obj21 ws1)

    (obj-at obj20 ws3)
    (obj-at obj22 ws3)

    (obj-at obj23 ws8)
    (obj-at obj25 ws8)

    (obj-at obj24 sh2)
))
)
