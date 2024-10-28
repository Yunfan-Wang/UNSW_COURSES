set terminal png size 900,600
set output 'throughput.png'

set xlabel "Time (s)"
set ylabel "Throughput (Mbps)"

set title "Throughput over Time for TCP Flows to n5"
set key outside bottom right

plot "tcp1.tr" using 1:2 with linespoints title "Flow 1 to n5" lw 2 pt 7, \
     "tcp2.tr" using 1:2 with linespoints title "Flow 2 to n5" lw 2 pt 7

pause -1
