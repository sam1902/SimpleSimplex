# Simple Simplex
## Purpose

[Wikipedia page of the Simplex Algorithm implemented by this program](https://www.wikiwand.com/en/Simplex_algorithm)

The purpose of this script is mostly educational. I couldn't find any implementation of the simplex algorithm that would fit the basic wikipedia's description and at the same time be easy to read.

All the implementations I came across were either too advanced (and hence not good for fundamental understanding), or too simplistic and messy with a pethora of for loops and cascading conditions.

## Design principle
This solver isn't written to be fast, or even very reliable, but rather could be seen as an example of wikipedia's excellent descrirption of the [Simplex Algorithm](https://www.wikiwand.com/en/Simplex_algorithm#/Algorithm). It just touches on the basics but by doing so it's easily debuggable and understandable to someone seeing it for the first time.

## Usage
As this isn't meant to be used by anyone for something other than education, it doesn't implement any form of automatic problem formulation whereby one would enter the constraints, objective and free variables. Instead you have to do it yourself, but it's a pretty straightforward process.

This algorithm internally handles a so called *"Simplex Tableau"*, which is a fancy way to represent the problem. It also need an objective function (but it's not really used to solve the problem in itself, it's just for displaying the results).

Many examples are included in the program, just uncomment one and you'll be able to test it out.

## Example
Given the following linear problem:

```
max z = 3*x1 + 4*x2
with the following constraints:
| x1 <= 8
| x2 <= 6
| -x1 + x2 <= 4
| x1 - x2 <= 7
| x1 + 2*x2 <= 16
and
x1 >= 0 
x2 >=0
```

First you have to put thi in standard form like so:

```
max z = 3*x1 + 4*x2
with the following constraints:
| x1 + s1 == 8
| x2 + s2 == 6
| -x1 + x2 + s3 == 4
| x1 - x2 + s4 == 7
| x1 + 2*x2 + s5 == 16
and
x1 >= 0 
x2 >=0
s1,2,3,4,5 >= 0
```

And then find the associated matix `A`, and vectors `X`, `c` and `b`:

```
X = [ x1, x2, s1, s2, s3, s4, s5 ]
A =
[[ 1,  0,  1,  0,  0,  0,  0],
 [ 0,  1,  0,  1,  0,  0,  0],
 [-1,  1,  0,  0,  1,  0,  0],
 [ 1, -1,  0,  0,  0,  1,  0],
 [ 1,  2,  0,  0,  0,  0,  1]]
b = [ 8, 6, 4, 7, 16 ]
// since max z = 3*x1 + 4*x2
//   <=> min z = -3 * x1 -4 * x2 
c = [ -3, -4, 0, 0, 0 ]
```

When you do so, you can formulate your problem as:

`max c^T • X  such that AX = b`

(Where `c^T` is the transpose of `c` so to make it a line vector.)

But the solver needs the [simplex tableau](https://www.wikiwand.com/en/Simplex_algorithm#/Simplex_tableau):

```
T = 
[[ 1, -c^T, 0 ],
 [ 0,    A, b ]]
```

Which in this case is:

```
canonical_tableau = 
[[1,  3,  4,  0,  0,  0, 0, 0, 0],
 [0,  1,  0,  1,  0,  0, 0, 0, 8],
 [0,  0,  1,  0,  1,  0, 0, 0, 6],
 [0, -1,  1,  0,  0,  1, 0, 0, 4],
 [0,  1, -1,  0,  0,  0, 1, 0, 7],
 [0,  1,  2,  0,  0,  0, 0, 1, 16]]
```

You also need to tell the system that the non basic variables (`x1` and `x2` in this instance) are in column 1 and 2 by setting `non_basic_cols = [1, 2]`.

Then the system will perform the simplex on this and print either *the* or *one* optimum if one exists, and if not it'll tell you that the problem is unbounded etc.

You can then enter the problem's simplex tableau, `non_basic_cols` and `objective` function in the beginning of the `main` function and run the program with:

```bash
python3 simplex_simplex.py [-v]
```

The `-v` option will mark a pause between each iteration to let you time to follow along on paper. 
