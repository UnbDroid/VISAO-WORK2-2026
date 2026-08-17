(define (problem amt-instance) (:domain robocup-work-transport)
(:objects 
    robot1 - robot

    start pp - location

    s1 s2 s3 - slot

    obj1 obj2 obj3 obj4 obj5 obj6 - object
)

(:init
    (at-robot robot1 start)
    (slot-free robot1 s1)
    (slot-free robot1 s2)
    (slot-free robot1 s3)

    (obj-at obj1 pp)
    (obj-at obj2 pp)
    (obj-at obj3 pp)
    (obj-at obj4 pp)
    (obj-at obj5 pp)
    (obj-at obj6 pp)
)

(:goal (and
    (obj-at obj1 pp)
    (obj-at obj2 pp)
    (obj-at obj3 pp)
    (obj-at obj4 pp)
    (obj-at obj5 pp)
    (obj-at obj6 pp)
))
)
