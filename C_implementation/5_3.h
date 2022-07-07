class _5_3: public dprfb {

 public:
  
  char *get_filter_name() {
    return (char *)"5/3 (Lineal) Biorthogonal Perfect Reconstruction Filter Bank";
  }

  void even_analyze(int /* dim */, int /* s */[], int /* l */[], int /* h */[]) throw();
  void odd_analyze(int /* dim */, int /* s */[], int /* l */[], int /* h */[]) throw();
  void even_synthesize(int /* dim */, int /* s */[], int /* l */[], int /* h */[]) throw();
  void odd_synthesize(int /* dim */, int /* s */[], int /* l */[], int /* h */[]) throw();

};
