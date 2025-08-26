## FJSP datasets
- 001-021: Barnes
- 022-031: Brandimarte (Mk#)
- 032-049: Dauzere-Paulli (#a)
- 050-069: Fattahi (SFJS# + MFJS#)
- 070-135: Hurink/edata (abz# + car# + la# + mt# + orb#)
- 136-201: Hurink/rdata (abz# + car# + la# + mt# + orb#)
- 202-267: Hurink/vdata (abz# + car# + la# + mt# + orb#)
- 268-271: Kacem (Kacem#)
- 272-331: Behnke (#)
- 332-427: Naderi (#)

## APP datasets
Same numbering as FJSP datasets.

Originally, the first job of instance la01 from Hurink's edata looks like this:
```
5 1 2 21 1 1 53 1 5 95 1 4 55 2 3 34 5 34
```
This job consists of 5 tasks; the first four can be processed by one machine, while the last one can be processed by two.
To include APPs, we transform it like so:
```
3 5 1 2 21 1 1 53 1 5 95 1 4 55 2 3 34 5 34
3 1 3 5
3 1 2 3
5 1 2 3 4 5
```

We prepend the number of APPs to the job line (in this case 3); after the job line, as many lines follow with an APP. The first APP in this example consists of tasks 1, 3 and 5; the second of tasks 1, 2 and 3, while the third APP consists of tasks 1 through 5.

## SDST datasets
- 20 instances from Fattahi (SFJS# + MFJS#) with SDST from Hexaly.
- 20 instances from Hurink/edata (la21 - la40) with SDST from Azzouz et al.

## And-Or datasets
170 instances according to the description from Kis (2003). Unique format, requires parser included in `src/`.