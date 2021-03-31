(define pi 3.1415926)
;'dress length'
(define l 72)
;'dress waist' 
(define W 68)
;'dress shape'
(define h 30)
(define (abs x) (if (< x 0) (- x) x))
(define (square x) (* x x))
(define (sqrt x)
	(define (average x y) (/ (+ x y) 2))
	(define (good-enough? guess) (< (abs (- (square guess) x)) 0.001))
	(define (improve guess) (average guess (/ x guess)))
	(define (sqrt-iter guess) (if (good-enough? guess) guess (sqrt-iter (improve guess))))
	(sqrt-iter 1.0)
)

(define r (/ W (* 2 pi)))

(define sl_ (sqrt (+ (* h h) (* r r))))

(define alpha (/ W (* 2 sl_)))

(define l_ (* l (/ h sl_) ))

(define (acp x y) (list x y))

(define (acpbcp ax ay bx by) (list ax ay bx by))

(define (line a b) (list a b))

;(define (curve o r theta1 theta 2))

(define (skirtFront)
	(define waistLine (line (acp 0 0) (acp 1 0)))
	(define rightGeneratrix (line (acp 1 0) (acp 1 1))) 
	(define bottomLine (line (acp 1 1) (acp 0 1))) 
	(define leftGeneratrix (line (acp 0 1) (acp 0 0))) 
	(list waistLine rightGeneratrix bottomLine leftGeneratrix)
)

(display (skirtFront))(newline)

;
;(define skirtBack (skirtFront))
;
;(define skirtFront (skirtFront skirtBack ) )
;
;(define main skirtFront)
;
