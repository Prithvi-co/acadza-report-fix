import math
def chk(name, got, want, tol=0.01):
    ok = abs(got-want) <= tol*max(1,abs(want))
    print(('PASS' if ok else 'FAIL'), name, 'got', round(got,5), 'want', want)
    return ok

allok = True
def C(*a):
    global allok
    allok &= chk(*a)

# R001/2/3 LCR: 50 V (key C=130 wrong, correct A)
C('LCR V', math.hypot(40, 60-30), 50)
# R005 flux: n=1 (key 2 wrong)
C('flux n', ((1/2)*(1/2)+(1/8)*2)/(1/2), 1)  # total/(q/2e0)
# R033 sig figs: 6*7.203^2=311.299 -> 311.3 -> 10A=3113
C('10A', round(6*7.203**2,1)*10, 3113)
# R037 photoelectric stopping V
C('stopping', 12400/4000-2.0, 1.1)
# capacitor dielectric (unreported): V^2+V-30=0 -> 5
C('cap V', (-1+math.sqrt(1+120))/2, 5)
# R006 cube compression mm^3 with 10 cm side
C('cube dV', 7e6/1.4e11*(0.1**3)*1e9, 50)
# displacement current: C=k e0 A/d, i=C dV/dt
C('disp I uA', 10*8.85e-12*(1/0.001)*25*1e6, 2.2125)
# R031 wheels: 0.5*(pi/4)*t^2=2pi
C('wheels t', math.sqrt(4*math.pi/(math.pi/4)), 4)
# lenses (unreported): f_eq, P_each
f=1/(1/50+1/12.5); C('lens P each', (100/f)/2, 5)
# R004 gas pressure
C('gas P', (1/3)*9e-2*400**2, 4800)
# R029 friction mu
F=100-10  # solve: F-100mu=10; 2F-100mu=100 -> F=90, mu=0.8
C('mu', (F-10)/100, 0.8)
# R015 AC power cos90
C('AC P', 0, 0)
# R034 waves: I=2I0 cos^2(pi/4)=I0 (assertion TRUE)
C('waves I/I0', 2*math.cos(math.pi/4)**2, 1)
# silver gamma
C('gamma', 3*0.19/(100*100)*1e5, 5.7)
# R024 wall friction
C('friction', min(0.3*100, 2*10), 20)
# displacement method (unreported): ratio 16
x=math.sqrt(150*(150-96)); C('displ ratio', ((150+x)/(150-x))**2, 16)
# R021 mean life
C('tau', 3/math.log(8), 1.4427)
# X-ray/de Broglie KE (eV)
h=6.626e-34; m=9.109e-31; e=1.602e-19
lam=12400/24800*1e-10  # 0.5 angstrom
C('xray KE eV', (h/lam)**2/(2*m)/e, 600, 0.02)
# R044 sphere Vp-Vs = 7/8*16
C('sphere', 7/8*16, 14)
# R043 drops ratio
C('drops', 64/16, 4)
# R016 cube float side
C('float a', math.sqrt(800/2), 20)
# R009/10 COM
C('vcom', 10*14/14, 10)
# R014 half lives
C('halflife', 3*60, 180)
# R030 SHM amplitude: pi = A*(pi/8)*cos(pi/4)
C('SHM A', 8/math.cos(math.pi/4)/math.sqrt(2)*math.sqrt(2)/1, 8*math.sqrt(2))
# R028 projectile tan=4
C('proj', 4, 4)
# R032 YDSE shift cm
C('ydse cm', (1/5e-3)*(2e-3*0.5-1.5e-3*0.4)*100, 8)
# R018/19 de Broglie 0.3 nm -> 16.8 eV
C('deB 0.3nm eV', (h/3e-10)**2/(2*m)/e, 16.8, 0.02)
# R018/19 check: what KE would 5.47 A give? (the garbled step)
C('5.47A gives eV (NOT 16.8)', (h/5.47e-10)**2/(2*m)/e, 5.03, 0.02)
print('ALL PASS' if allok else 'SOME FAILED')
