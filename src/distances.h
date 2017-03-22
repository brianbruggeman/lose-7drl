#ifndef DISTANCES_H
#define DISTANCES_H
#include <Python.h>

// Standard distances
static PyObject* distances_manhattan_distance(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* distances_euclidean_distance(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* distances_octagonal_distance(PyObject* self, PyObject* args, PyObject* kwds);

#endif // DISTANCES_H