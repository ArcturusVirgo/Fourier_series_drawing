program main
    implicit none

    integer, parameter :: N_max = 2000, N_cal = 200, order = 25
    real(8), parameter :: pi = 3.1415926535, integrate_precision = 0.01
    integer i, j, k, m, N, N_integrate
    real(8) f, temp_1, temp_2, temp_3, temp_4
    real(8) an_x, bn_x, an_y, bn_y, x, t, tt, a0_x, a0_y
    real(8) init_x(N_max), init_y(N_max), init_t(N_max), f_x(N_cal), f_y(N_cal), t_cal(N_cal)

    N_integrate = int(2 * pi / integrate_precision)

    open(10, file = '.\..\..\1-get_points\result\鹿头.txt')
    open(11, file = '.\..\result\txt\鹿头-fortran.txt', status='replace')


    ! 读入数据并赋初始值
    i = 0
    300 i = i + 1
    read(10, *, end = 400) init_t(i), init_x(i), init_y(i)
    goto 300
    400 continue
    N = i - 1

    do i = 1, N_cal
        t = (i - 1) / real(N_cal - 1) * 2 * pi
        t_cal(i) = t

        ! 计算 a0_x, a0_y
        a0_x = f(0 * pi, init_t, init_x, N) + f(2 * pi, init_t, init_x, N)
        a0_y = f(0 * pi, init_t, init_y, N) + f(2 * pi, init_t, init_y, N)
        temp_1 = 0
        temp_2 = 0
        do k = 0, N_integrate - 2
            tt = k / real(N_integrate - 1) * 2 * pi
            temp_1 = temp_1 + f(tt, init_t, init_x, N)
            temp_2 = temp_2 + f(tt, init_t, init_y, N)
        end do
        a0_x = a0_x + 2 * temp_1
        a0_y = a0_y + 2 * temp_2
        temp_1 = 0
        temp_2 = 0
        do k = 0, N_integrate - 2
            tt = k / real(N_integrate - 1) * 2 * pi
            temp_1 = temp_1 + f(tt + integrate_precision / 2, init_t, init_x, N)
            temp_2 = temp_2 + f(tt + integrate_precision / 2, init_t, init_y, N)
        end do
        a0_x = a0_x + 4 * temp_1
        a0_y = a0_y + 4 * temp_2
        a0_x = a0_x * integrate_precision / 6 / pi
        a0_y = a0_y * integrate_precision / 6 / pi

        f_x(i) = a0_x / 2
        f_y(i) = a0_y / 2

        ! 计算 an_x, an_y
        do j = 1, order
            an_x = f(0 * pi, init_t, init_x, N) * cos(0.0) + f(2 * pi, init_t, init_x, N) * cos(j * 2 * pi)
            bn_x = f(0 * pi, init_t, init_x, N) * sin(0.0) + f(2 * pi, init_t, init_x, N) * sin(j * 2 * pi)
            an_y = f(0 * pi, init_t, init_y, N) * cos(0.0) + f(2 * pi, init_t, init_y, N) * cos(j * 2 * pi)
            bn_y = f(0 * pi, init_t, init_y, N) * sin(0.0) + f(2 * pi, init_t, init_y, N) * sin(j * 2 * pi)
            temp_1 = 0
            temp_2 = 0
            temp_3 = 0
            temp_4 = 0
            do k = 0, N_integrate - 2
                tt = k / real(N_integrate - 1) * 2 * pi
                temp_1 = temp_1 + f(tt, init_t, init_x, N) * cos(j * tt)
                temp_2 = temp_2 + f(tt, init_t, init_x, N) * sin(j * tt)
                temp_3 = temp_3 + f(tt, init_t, init_y, N) * cos(j * tt)
                temp_4 = temp_4 + f(tt, init_t, init_y, N) * sin(j * tt)
            end do
            an_x = an_x + 2 * temp_1
            bn_x = bn_x + 2 * temp_2
            an_y = an_y + 2 * temp_3
            bn_y = bn_y + 2 * temp_4
            temp_1 = 0
            temp_2 = 0
            temp_3 = 0
            temp_4 = 0
            do k = 0, N_integrate - 2
                tt = k / real(N_integrate - 1) * 2 * pi
                temp_1 = temp_1 + f(tt + integrate_precision / 2, init_t, init_x, N) * cos(j * tt)
                temp_2 = temp_2 + f(tt + integrate_precision / 2, init_t, init_x, N) * sin(j * tt)
                temp_3 = temp_3 + f(tt + integrate_precision / 2, init_t, init_y, N) * cos(j * tt)
                temp_4 = temp_4 + f(tt + integrate_precision / 2, init_t, init_y, N) * sin(j * tt)
            end do
            an_x = an_x + 4 * temp_1
            bn_x = bn_x + 4 * temp_2
            an_y = an_y + 4 * temp_3
            bn_y = bn_y + 4 * temp_4
            an_x = an_x * integrate_precision / 6 / pi
            bn_x = bn_x * integrate_precision / 6 / pi
            an_y = an_y * integrate_precision / 6 / pi
            bn_y = bn_y * integrate_precision / 6 / pi

            ! 计算一个点的结果
            f_x(i) = f_x(i) + an_x * cos(j * t) + bn_x * sin(j * t)
            f_y(i) = f_y(i) + an_y * cos(j * t) + bn_y * sin(j * t)
        end do
        ! 输出进度
        if (mod(i, 10)==0) then
            print *, i
        end if
    end do

    ! 写入进度
    do i = 1, N_cal
        write(11, *) t_cal(i), f_x(i), f_y(i)
    end do

end program main

! 线性插值函数
function f(x, data_x, data_y, N)
    implicit none
    integer i, N
    real(8) x, f
    real(8) data_x(N), data_y(N)

    do i = 1, N - 1
        if (x==data_x(i)) then
            f = data_y(i)
            exit
        elseif (x==data_x(i + 1)) then
            f = data_y(i + 1)
            exit
        elseif (x>data_x(i) .and. x< data_x(i + 1)) then
            f = (data_y(i + 1) - data_y(i)) / (data_x(i + 1) - data_x(i)) * (x - data_x(i)) + data_y(i)
            exit
        elseif (x>data_x(i + 1)) then
            f = data_y(i + 1)
        end if

    end do

end function f