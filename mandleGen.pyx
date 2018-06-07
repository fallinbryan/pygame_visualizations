from libc.math cimport sqrt
#import math

cdef int complex_abs(int real, int imag):
    real = real >> 1
    imag = imag >> 1
    return (real + imag) << 1


cdef double* complex_square(double z[]):
    cdef double rv[2]
    rv[0] =  z[0]*z[0] - z[1]*z[1]
    rv[1] = 2 * z[0] * z[1]
    return rv

cdef double* complex_add(double z[], double c[]):
    cdef double rv[2]
    rv[0] = z[0] + c[0]
    rv[1] = z[1] + c[1]
    return rv

cpdef double  map(double value, double current_value_lower_bound, double current_value_upper_bound,
        double target_value_lower_bound, double target_value_upper_bound):
    cdef double current_range = current_value_upper_bound - current_value_lower_bound
    cdef double target_range = target_value_upper_bound - target_value_lower_bound
    cdef double return_value = (((value - current_value_lower_bound)*target_range)/current_range) + target_value_lower_bound
    return return_value


cpdef list render_mandlebrot(x_min, x_max, y_min, y_max, disp_h, disp_w):
    cdef list MAP = []
    cdef int y
    cdef int x
    cdef int n
    cdef int r
    cdef int g
    cdef int b

    cdef double c[2]
    cdef double z[2]

    for y in range(disp_h):
        for x in range(disp_w):
            z[0] = c[0] = map(x, 0, disp_w, x_min, x_max)
            z[1] = c[1] = map(y, 0, disp_h, y_min, y_max)
            #c = z = complex(c_real, c_imag)
            n = 0
            while n < 100:
                    #z = z**2 + c
                    z = complex_square(z)
                    z = complex_add(z,c)
                    n += 1
                    #if abs(z) > 4.0:
                    if complex_abs(int(z[0]), int(z[1])) > 8:
                        break

            r = int(map(n, 0, 100, 0, 255))
            g = int(map(n, 0, 100, 0, 255))
            b = int(map(n, 0, 100, 0, 255))


            r = 255 - r
            g = 255 - g
            b = 255 - b

            MAP.append(((x, y), (r, g, b)))

    return MAP
