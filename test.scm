(define x1 2)
(define x2 5)
;
(define (r x ) (* x1 (+ x2 x)) )
(define (r2 x) (* (r 4) x))
(define (r1 x y) (* x (* x y)) )

;(r1 3 x1)
;(r1 (r x1) (r2 x2))
;
;
;(list
;    (list (- (+ (ln x1) (* x1 x2) ) (sin x2)) )
;    (+ x1 x2)
;    (* (r 4) x2)
;    (+ x1 3)
;    (+ x1 3)
;    (+ r 3)
;)

(- (+ (ln x1) (* x1 x2) ) (sin x2))

;(* x1 x2)

