// aa_example.c
void foo(int *a, int *b, int n) {
  for (int i = 0; i < n; i++) {
    a[i] = b[i] + 1;
  }
}

