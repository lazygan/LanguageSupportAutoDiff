(define x1 3)
(define x2 5)

(define (r3 x) (* x1 (+ x2 x)) )

(define (sqrt x) (* x x) )

;(+ x1 4)
(define (r4 x) (* (r3 4) x))
(r3 4)
(sqrt (r4 3))

;(list
;    (list (- (+ (ln x1) (* x1 x2) ) (sin x2)) )
;    (+ x1 x2)
;    (* (r3 4) x2)
;    (+ x1 3)
;    (+ x1 3)
;    (+ r3 3)
;    ;(sqrt x1)
;)


