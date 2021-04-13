(define (main)
    (define x1 2)
    (define x2 5)
    (define (r1 x y)
        (define (r x )
            (define (r3 x) (+ x2 x) )
            (* x1 (r3 x) )
        )
        (define (r2 x) (* (r 4) x))
        (* (r x) (* (r x) (r2 y)))
    )
    (r1 x1 x2)
)
;(r1 3 x1)
;(- (+ (ln x1) (* x1 x2) ) (sin x2))

(main)


