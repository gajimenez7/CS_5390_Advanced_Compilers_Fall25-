int inc(int *x) { (*x)++; return *x; }
void bar(int *a, int *b) { *a = inc(b); }

