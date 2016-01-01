#include <stdio.h>
#include "dprfb.h"
#include "IO.h"

void IO::even_analyze(int n, int s[], int l[], int h[]) throw() {
  int i;
  for(i=0; i<n/2; i++) {
    h[i] = s[i<<1];
  }
  fwrite(h, sizeof(int), n/2, stdout);
}

void IO::odd_analyze(int n, int s[], int l[], int h[]) throw() {
  int i;
  for(i=0; i<n/2; i++) {
    h[i] = s[i<<1];
  }
  fwrite(h, sizeof(int), n/2, stdout);
}

void IO::even_synthesize(int n, int s[], int l[], int h[]) throw() {
  int i;
  fread(h, sizeof(int), n/2, stdin);
  for(i=0; i<n/2; i++) {
    s[i<<1] = h[i];
  }
}

void IO::odd_synthesize(int n, int s[], int l[], int h[]) throw() {
  int i;
  fread(h, sizeof(int), n/2, stdin);
  for(i=0; i<n/2; i++) {
    s[i<<1] = h[i];
  }
}
