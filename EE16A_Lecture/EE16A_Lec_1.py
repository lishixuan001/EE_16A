%% Head GSI %%:
olivia-ee16a@berkeley.edu
--Questions not for piazza
--Conflicts
--Emergencies

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Policies %%:
Go to every lecture and discussion
1 lab each week can be dropped

APE: 3%
Homework: 15%
Labs: 15%
Midterm1: July 11__17%
Midterm2: july 28__17%
Final: Aug 11__33%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Input-Output %%
input and output light intensities: (w/m^2)
a: path length for the light(m)
x: attention coeff(1/m)
I(out)/I(in) = e^ax (x is unknown)

Bougrer(1729)-Lambert(1760)-Beer Law(1852)

By taking ln() on both sides
ln(I(out)/I(in)) = -ax/(-1) ==> ln(I(in)/I(out))) [we call this 'b']

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Extend %%:
           a1   a2   a3         an 
I(in)----> x1 | x2 | x3 | ... | xn ----> I(out)
              I1   I2   I3 I(n-1)

I(out)/I(n-1) = e^-a(n)x(n)
I(n-1)/I(n-2) = e^-a(n-1)x(n-1)
I(1)/I(in) = e^-a(1)x(1)

Multiply together
===>  I(out)/I(in) = e^-a(1)x(1) * e^-a(2)x(2) * ... * e^-a(n)x(n)
===> ln(I(out)/I(in)) = -a(1)x(1)-a(2)x(2)-...-a(n)x(n)/(-1)
===> ln(I(in)/I(out)) = a(1)x(1)+a(2)x(2)+...-+(n)x(n)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Extend2 %%:
 -      |    |
     -  |    |
---->  x1    x2  ----> b1 (coresponding to the previous b)
---->  x3    x4  ----> b2
        |    | -
        |    |   -
        b3  b4*    b4

experiments          measurements
-----------------    -----
x1 + x2            = b1   (E1)
          x3 + x4  = b2   (E2)
x1      + x3       = b3   (E3)
     x2      + x4  = b4*  (E4*)
x1           + x4  = b4   (E4)

Problems:
    x(water) = 0
    x(juice) = 1/2
    x(milk)  = 1
    
0  1        1/2   1/2
1  0   vs   1/2   1/2

both has a result of:
b1   1 | 1 | 
b2   1 | 1 |
b3   1 | 1 |
b4*  1 | 1 |
b4   0 | 1 |


E1 + E2 - E3 ===> x1 + x2 + x3 + x4 - x1 - x3 ===> x2 + x4 ===> E4*
(Redundancy since we can get E4* from E1/E2/E3)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

&& Q: Given a set of experiments, is there reducdancy?
&& A: Gaussian Elimination

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


































