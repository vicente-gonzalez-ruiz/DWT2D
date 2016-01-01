/*
 * The 2D Discrete Wavelet Transform.
 * gse. 2006.
 */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include "mallok.h"
#include "dprfb.h"
#include "Haar.h"
#include "5_3.h"
#include "13_7.h"
#include "SP.h"
//#include "IO.h"
#include "dwt2d.h"

int main(int argc, char *argv[]) {

  char *filter_name = (char *)"5/3";
  int inverse = 0;
  int pixels_in_y = 288;
  int pixels_in_x = 352;
  int levels = 3;
  int by_resolutions = 0;
  
  int c;
  while (1) {

    static struct option long_options[] = {
      {"filter_name", required_argument, 0, 'f'},
      {"levels", required_argument, 0, 'l'},
      {"inverse", no_argument, 0, 'i'},
      {"pixels_in_y", required_argument, 0, 'y'},
      {"pixels_in_x", required_argument, 0, 'x'},
      {"by_resolutions", required_argument, 0, 'b'},
      {"help", no_argument, 0, '?'},
      {0, 0, 0, 0}
    };

    int option_index = 0;

    c = getopt_long(argc, argv, "f:l:iy:x:b?", long_options, &option_index);

    if(c==-1) {
      /* Ya no hay más opciones. */
      break;
    }

    switch (c) {

    case 0:
      /* If this option set a flag, do nothing else now. */
      if (long_options[option_index].flag != 0)
	break;
      fprintf(stderr, "option %s", long_options[option_index].name);
      if (optarg)
	fprintf(stderr, " with arg %s", optarg);
      fprintf(stderr, "\n");
      break;
      
    case 'f':
      filter_name = optarg;
      fprintf(stderr, "%s: filter_name=%s\n", argv[0], filter_name);
      break;

    case 'l':
      levels = atoi(optarg);
      fprintf(stderr, "%s: levels=%d\n", argv[0], levels);
      break;

    case 'i':
      inverse = 1;
      fprintf(stderr, "%s: inverse transform\n", argv[0]);
      break;

    case 'y':
      pixels_in_y = atoi(optarg);
      fprintf(stderr, "%s: pixels_in_y=%d\n", argv[0], pixels_in_y);
      break;

    case 'x':
      pixels_in_x = atoi(optarg);
      fprintf(stderr, "%s: pixels_in_x=%d\n", argv[0], pixels_in_x);
      break;

    case 'b':
      by_resolutions = 1;
      fprintf(stderr, "%s: writing/reading coefs by spatial resolutions\n", argv[0]);
      break;

    case '?':
      fprintf(stderr, "Discrete Wavelet Transform of int images.\n");
      fprintf(stderr, "\n");
      fprintf(stderr, "Parameters:\n");
      fprintf(stderr, "\n");
      fprintf(stderr, "  -[-f]ilter_name = name of the filter {Haar|5/3|S+P|13/7} (\"%s\")\n", filter_name);
      fprintf(stderr, "  -[-l]evels = number of levels of the DWT (%d)\n", levels);
      fprintf(stderr, "  -[-i]nverse transform (%d)\n", inverse);
      fprintf(stderr, "  -[-]pixels_in_[x] = size of the X dimension of the pictures (%d)\n", pixels_in_x);
      fprintf(stderr, "  -[-]pixels_in_[y] = size of the Y dimension of the pictures (%d)\n", pixels_in_y);
      fprintf(stderr, "  -[-b]y_resolutions (%d)\n", by_resolutions);
      printf("\n");
      exit(1);
      break;
      
    default:
      fprintf(stderr, "%s: Unrecognized argument. Aborting ...\n", argv[0]);
      abort();
    }
  }

  int max_Y_X;
  if(pixels_in_y>pixels_in_x) max_Y_X = pixels_in_y; else max_Y_X = pixels_in_x;
  dwt2d dwt;
  dwt.set_max_line_size(max_Y_X);
  
  class mallok malloc;
  int **data = (int **)malloc.alloc_2d(pixels_in_y, pixels_in_x, sizeof(int));
  
  class dprfb *filter;

  switch((int)filter_name[0]) {
  case 'H'/*aar*/:
    //dwt.set_filter(new class Haar());
    filter = new class Haar();
    break;

  case 'S'/*P*/:
    filter = new class SP();
    //dwt.set_filter(new class SP());
    break;

  case '5':
    filter = new class _5_3();
    //dwt.set_filter(new class _5_3());
    break;

  case '1':
    filter = new class _13_7();
    //dwt.set_filter(new class _13_7());
    break;

  default:
    fprintf(stderr,"%s: undefined filter\n", argv[0]);
  }

  fprintf(stderr,"%s: using %s\n", argv[0], filter->get_filter_name());

  int *y_limits = (int *)malloc.alloc_1d(sizeof(int), levels);
  int *x_limits = (int *)malloc.alloc_1d(sizeof(int), levels);

  if(by_resolutions) {
    y_limits[0] = pixels_in_y;
    x_limits[0] = pixels_in_x;
    for(int l=1; l<=levels; l++) {
      y_limits[l] = (y_limits[l-1] + 1) / 2;
      x_limits[l] = (x_limits[l-1] + 1) / 2;
      fprintf(stderr,"%d %d\n",y_limits[l], x_limits[l]);
    }
  }
  
  if(!inverse) {
    fprintf(stderr, "%s: direct transform\n", argv[0]);

    fprintf(stderr,"%s: reading data\n",argv[0]);
    int y;
    for(y=0; y<pixels_in_y; y++) {
      fread(data[y], sizeof(int), pixels_in_x, stdin);
    }
 
    dwt.set_filter(filter);
    dwt.analyze(data, pixels_in_y, pixels_in_x, levels);

    if(by_resolutions) {
      // Write LL
      for (int y=0; y<y_limits[levels]; y++) {
	fwrite(data[y], sizeof(int), x_limits[levels], stdout);
      }
      
      // Write the rest of subbands
      for (int l=levels; l>0; l--) {
	
	// LH (down, left)
	for (int y=y_limits[l]; y<y_limits[l-1]; y++) {
	  fwrite(data[y], sizeof(int), x_limits[l], stdout);
	}
	
	// HL (up, right)
	for (int y=0; y<y_limits[l]; y++) {
	  fwrite(data[y]+x_limits[l], sizeof(int), x_limits[l-1] - x_limits[l], stdout);
	}
	
	// HH
	for (int y=y_limits[l]; y<y_limits[l-1]; y++) {
	  fwrite(data[y]+x_limits[l], sizeof(int), x_limits[l-1] - x_limits[l], stdout);
	}
	
      }
    } /* by resultions */ else {
      for(int y=0; y<pixels_in_y; y++) {
	fwrite(data[y], sizeof(int), pixels_in_x, stdout);
      }
    }
    
  } else {
    fprintf(stderr,"%s: inverse transform\n",argv[0]);
    
    if(by_resolutions) {
      // Read LL
      for (int y=0; y<y_limits[levels]; y++) {
	fread(data[y], sizeof(int), x_limits[levels], stdin);
      }
      
      // Read the rest of subbands
      for (int l=levels; l>0; l--) {
	
	// LH (down, left)
	for (int y=y_limits[l]; y<y_limits[l-1]; y++) {
	  fread(data[y], sizeof(int), x_limits[l], stdin);
	}
	
	// HL (up, right)
	for (int y=0; y<y_limits[l]; y++) {
	  fread(data[y]+x_limits[l], sizeof(int), x_limits[l-1] - x_limits[l], stdin);
	}
	
	// HH
	for (int y=y_limits[l]; y<y_limits[l-1]; y++) {
	  fread(data[y]+x_limits[l], sizeof(int), x_limits[l-1] - x_limits[l], stdin);
	}
	
      }
    } /* by_resolutions*/ else {
      for(int y=0; y<pixels_in_y; y++) {
	fread(data[y], sizeof(int), pixels_in_x, stdin);
      }
    }

    dwt.set_filter(filter);
    dwt.synthesize(data, pixels_in_y, pixels_in_x, levels);

    fprintf(stderr,"%s: writing data\n",argv[0]);
    int y;
    for(y=0; y<pixels_in_y; y++) {
      fwrite(data[y], sizeof(int), pixels_in_x, stdout);
    }

  }
}

