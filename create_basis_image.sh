~/bin/dwt2d_basis -f $1 -l 4 -x 1024 -y 1024 > /tmp/1
int2float < /tmp/1 > /tmp/2
normalize float < /tmp/2 > /tmp/3
mult float 255 < /tmp/3 > /tmp/4
float2uchar < /tmp/4 > /tmp/5
rawtopgm 1024 1024 < /tmp/5 > /tmp/5.pgn
display /tmp/5.pgn &

