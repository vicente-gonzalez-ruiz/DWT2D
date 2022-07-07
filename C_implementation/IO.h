class IO: public dprfb {

 public:
  
  char *get_filter_name() {
    return (char *)"Write to stdout (analyze) and read from stdin (synthesize) DWT coefficients using the subband order";
  }

  void even_analyze   (int items_in_signal, int signal[], int low[], int high[]) throw();
  void odd_analyze    (int items_in_signal, int signal[], int low[], int high[]) throw();
  void even_synthesize(int items_in_signal, int signal[], int low[], int high[]) throw();
  void odd_synthesize (int items_in_signal, int signal[], int low[], int high[]) throw();

};
