from libc.math cimport sqrt, log
#import math

cdef long double complex_abs(long double real, long double imag):
    return sqrt(real*real + imag*imag)


cdef long double* complex_square(long double z[]):
    cdef long double rv[2]
    rv[0] =  z[0]*z[0] - z[1]*z[1]
    rv[1] = 2 * z[0] * z[1]
    return rv

cdef long double* complex_add(long double z[], long double c[]):
    cdef long double rv[2]
    rv[0] = z[0] + c[0]
    rv[1] = z[1] + c[1]
    return rv

cpdef long double  map(long double value, long double current_value_lower_bound, long double current_value_upper_bound,
        long double target_value_lower_bound, long double target_value_upper_bound):
    cdef long double current_range = current_value_upper_bound - current_value_lower_bound
    cdef long double target_range = target_value_upper_bound - target_value_lower_bound
    cdef long double return_value = (((value - current_value_lower_bound)*target_range)/current_range) + target_value_lower_bound
    return return_value


cpdef list render_mandlebrot(x_min, x_max, y_min, y_max, disp_h, disp_w):
    cdef list MAP = []
    cdef int y
    cdef int x
    cdef int n
    cdef int r
    cdef int g
    cdef int b
    cdef int color

    cdef long double c[2]
    cdef long double z[2]
    cdef long double z_abs

    for y in range(disp_h):
        for x in range(disp_w):
            z[0] = c[0] = map(x, 0, disp_w, x_min, x_max)
            z[1] = c[1] = map(y, 0, disp_h, y_min, y_max)
            #c = z = complex(c_real, c_imag)
            n = 0
            while n < 255:
                    #z = z**2 + c
                    z = complex_square(z)
                    z = complex_add(z,c)
                    n += 1
                    #if abs(z) > 4.0:
                    z_abs = complex_abs(z[0], z[1])
                    if z_abs > 4.0:
                        break

            if n < 254:
                r = n
                g = 0
                b = n
                a = n

            else:
                r = 0
                g = 0
                b = 0
                a = n
            #r = 255 - r
            #g = 255 - g
            #b = 255 - b




            MAP.append(((x, y), (r, g, b, a)))
            #MAP.append( ((x, y),(color)) )

    return MAP
