(define (problem btt1-intance) (:domain robocup-work-transport)
(:objects
    robot1 - robot

    start ws3 ws4 - location

    s1 s2 s3 - slot

    obj1 obj3 obj5 obj6 - object
)

(:init
    (at-robot robot1 start)
    (slot-free robot1 s1)
    (slot-free robot1 s2)
    (slot-free robot1 s3)

    (obj-at obj1 ws3)
    (obj-at obj3 ws3)
    (obj-at obj5 ws3)
    (obj-at obj6 ws3)
)

(:goal (and
    (obj-at obj1 ws4)
    (obj-at obj3 ws4)
    (obj-at obj5 ws4)
    (obj-at obj6 ws4)
)
)
)
