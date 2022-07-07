#!/bin/sh

filter_name="5/3"
levels=1
pixels_in_y=288
pixels_in_x=352

usage() {
    echo $0
    echo "  [-f (filter_name, $filter_name by default)]"
    echo "  [-l (levels, $levels by default)]"
    echo "  [-x (pixels_in_x, $pixels_in_x by default)]"
    echo "  [-y (pixels_in_y, $pixels_in_y by default)]"
    echo "  [-? (help)]"
}

echo $0: parsing: $@ >&2

while getopts "f:l:x:y:?" opt; do
    case ${opt} in
        f)
	    filter_name="${OPTARG}"
	    ;;
        l)
	    levels="${OPTARG}"
	    ;;
        x)
	    pixels_in_x="${OPTARG}"
	    ;;
        y)
	    pixels_in_y="${OPTARG}"
	    ;;
        ?)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -${OPTARG}" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -${OPTARG} requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

set -x

uchar2int < /dev/stdin > /tmp/1

number_of_zeros=`echo "($pixels_in_y*(2^$levels)*$pixels_in_x*(2^$levels) - $pixels_in_y*$pixels_in_x)*4" | bc -l`

dd if=/dev/zero of=/tmp/2 count=4 bs=$number_of_zeros
cat /tmp/1 /tmp/2 > /tmp/3
rm /tmp/1 /tmp/2

Y=`echo "$pixels_in_y*(2^$levels)" | bc -l`
X=`echo "$pixels_in_x*(2^$levels)" | bc -l` 

dwt2d --by_resolutions --filter_name=$filter_name --levels=$levels --inverse --pixels_in_y=$Y --pixels_in_x=$X < /tmp/3 > /tmp/4
rm /tmp/3

int2uchar < /tmp/4 > /dev/stdout
rm /tmp/4

set +x
