// alias_cases.c
void bar(int *p, int *q, int n) {
  int *r = p + 1;
  int *s = p + 2;
  *p = *q; // possibly alias if q == p
  *r = *s; // guaranteed no overlap (p+1, p+2 point to different ints)
}
