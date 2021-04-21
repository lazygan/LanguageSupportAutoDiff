(define x1 2)
(define x2 5)
(- (+ (ln x1) (* x1 x2) ) (sin x2))
;17640 31500 10528
(define (main x y)
    (define (r1 x y)
        (define (r a)
            (define (r3 a) (+ x2 a) )
            (* x1 (r3 a) )
        )
        (define (r2 b) (* (r 4) b))

        (* (r2 y) (* (r x)  (r x)))
    )
    (r1 x y)
)
(main x1 x2)



