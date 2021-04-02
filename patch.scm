(in l "dress length" 0.4 60 120)

(in w "dress waist"  0.3 60 120)

(in h "dress shape"  0.2 20 50)


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

(define (curveFitCircle ox oy r theta1 theta2 clockwise)
    (define dtheta (- theta2 theta1))
    (define bzr (* r (tan (/ dtheta 4))))
    (define acpx1 (+ ox (* r (cos theta1))))
    (define acpy1 (+ oy (* r (sin theta1))))
    (define acpx2 (+ ox (* r (cos theta2))))
    (define acpy2 (+ oy (* r (sin theta2))))

    (define bcpx1 (- acpx1 (* bzr (sin theta1))))
    (define bcpy1 (+ acpy1 (* bzr (cos theta1))))
    (define bcpx2 (+ acpx2 (* bzr (sin theta2))))
    (define bcpy2 (- acpy2 (* bzr (cos theta2))))
    (if (eq? clockwise 0)
        (curve (acpbcp acpx1 acpy1 bcpx1 bcpy1 ) (acpbcp acpx2 acpy2 bcpx2 bcpy2))
        (curve (acpbcp acpx2 acpy2 bcpx2 bcpy2) (acpbcp acpx1 acpy1 bcpx1 bcpy1 ))
    )
)

(define (lineByTheta ox oy r1 r2 theta dir)
    (define acp1x (+ ox (* r1 (cos theta))))
    (define acp1y (+ oy (* r1 (sin theta))))
    (define acp2x (+ ox (* r2 (cos theta))))
    (define acp2y (+ oy (* r2 (sin theta))))
    (if (eq? dir 0)
        (line ( acp acp1x acp1y) (acp acp2x acp2y))
        (line ( acp acp2x acp2y) (acp acp1x acp1y))
    )
)

(define (skirtFront)
    (define ox 0.1)
    (define oy 0.1)
    (define theta1 0)
    (define theta2 alpha)
    (define r1 sl_)
    (define r2 (+ sl_ l))
	(define waistLine (curveFitCircle ox oy r1 theta1 theta2 0))
	(define rightGeneratrix (lineByTheta ox oy r1 r2 theta2 0))
	(define bottomLine (curveFitCircle ox oy r2 0 theta2 1))
	(define leftGeneratrix (lineByTheta ox oy r1 r2 theta1 1))
	(list waistLine rightGeneratrix bottomLine leftGeneratrix)
)



(define skirtBack (skirtFront))
(define main (skirtFront))

(out main)
