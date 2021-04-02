(in l "dress length" 72 60 120)

(in w "dress waist"  68 60 120)

(in h "dress shape"  30 20 50)


(define pi 3.1415926)
(define (abs x) (if (< x 0) (- x) x))
(define (square x) (* x x))
(define (sqrt x)
	(define (average x y) (/ (+ x y) 2))
	(define (good-enough? guess) (< (abs (- (square guess) x)) 0.001))
	(define (improve guess) (average guess (/ x guess)))
	(define (sqrt-iter guess) (if (good-enough? guess) guess (sqrt-iter (improve guess))))
	(sqrt-iter 1.0)
)

(define r (/ w (* 2 pi)))

(define sl_ (sqrt (+ (* h h) (* r r))))

(define alpha (/ w (* 2 sl_)))

(define l_ (* l (/ h sl_) ))

(define (acp x y) (list x y))

(define (acpbcp ax ay bx by) (list ax ay bx by))

(define (line a b) (list a b))
(define (curve a b) (list a b))

;(define (curve o r theta1 theta 2))
;(define (line o r theta1 theta 2))

(define (skirtFront)
	(define waistLine (curve (acpbcp 0.1 0.1 0.2 0.2) (acpbcp 0.6 0.1 0.5 0.2)))
	(define rightGeneratrix (line (acp 0.6 0.1) (acp 0.6 0.6)))
	(define bottomLine (curve (acpbcp 0.6 0.6 0.5 0.5) (acpbcp 0.1 0.6 0.2 0.5)))
	(define leftGeneratrix (line (acp 0.1 0.6) (acp 0.1 0.1)))
	(list waistLine rightGeneratrix bottomLine leftGeneratrix)
)



(define skirtBack (skirtFront))
(define main (skirtFront))

(out main)
