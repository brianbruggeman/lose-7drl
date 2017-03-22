#include <math.h>
#include <limits.h>
#include <Python.h>
#include "distances.h"


static char* extract_repr(PyObject* obj) {
    PyObject* obj_repr = PyObject_Repr(obj);
    char* obj_str = PyUnicode_AsUTF8(obj_repr);
    Py_DECREF(obj_repr);
    return obj_str;
}

// Utility function for displaying an arbitrary python object
void display_python_object(char* string, PyObject* obj) {
    const char* obj_str = extract_repr(obj);
    printf("%s: %s\n", string, obj_str);
}


static PyObject* distances_manhattan_distance(PyObject* self, PyObject* args, PyObject* kwds) {
    // diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    PyObject* point_x;
    PyObject* point_y;
    int point_x_length = -1;
    int point_y_length = -1;
    double val_x = 0.0;
    double val_y = 0.0;
    int max_dim = -1;
    double diff = 0;
    double return_value = 0;
    static char *kws[] = { "x", "y", NULL };

    // Validate that the input correctly corresponds to the expected signature
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kws, &point_x, &point_y)) {
        return NULL;
    }

    // Find the maximum length
    point_x_length = Py_SIZE(point_x);
    point_y_length = Py_SIZE(point_y);
    max_dim = point_x_length;
    if (point_x_length < point_y_length) {
        max_dim = point_y_length;
    }

    // Iterate over each value and perform sum += abs(x(i) - y(i))
    // where
    //     if x(i) does not exist, then x(i) = 0
    //     and if y(i) does not exist, then y(i) = 0
    for (int i=0; i<max_dim; i++) {
        val_x = 0;
        val_y = 0;
        diff = 0;
        // extract point x value
        if (i < point_x_length) {
            PyObject* x = PyTuple_GetItem(point_x, i);
            val_x = PyFloat_AsDouble(x);
        }
        // extract point y value
        if (i < point_y_length) {
            PyObject* y = PyTuple_GetItem(point_y, i);
            val_y = PyFloat_AsDouble(y);
        }
        // Calculate difference
        if (val_x < val_y) {
            diff = val_y - val_x;
        } else {
            diff = val_x - val_y;
        }
        return_value += diff;
    }
    return Py_BuildValue("d", return_value);
}

static PyObject* distances_euclidean_distance(PyObject* self, PyObject* args, PyObject* kwds) {
    // diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    // distance = math.sqrt(sum(diff**2 for diff in diffs))

    PyObject* point_x;
    PyObject* point_y;
    int point_x_length = -1;
    int point_y_length = -1;
    double val_x = 0.0;
    double val_y = 0.0;
    int max_dim = -1;
    double diff = 0;
    double return_value = 0;
    static char *kws[] = { "x", "y", NULL };

    // Validate that the input correctly corresponds to the expected signature
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kws, &point_x, &point_y)) {
        return NULL;
    }

    // Find the maximum length
    point_x_length = Py_SIZE(point_x);
    point_y_length = Py_SIZE(point_y);
    max_dim = point_x_length;
    if (point_x_length < point_y_length) {
        max_dim = point_y_length;
    }

    // Iterate over each value and perform sum += (x(i) - y(i))^2
    // where
    //     if x(i) does not exist, then x(i) = 0
    //     and if y(i) does not exist, then y(i) = 0
    for (int i=0; i<max_dim; i++) {
        val_x = 0;
        val_y = 0;
        diff = 0;
        // dereference and extract value
        if (i < point_x_length) {
            PyObject* x = PyTuple_GetItem(point_x, i);
            val_x = PyFloat_AsDouble(x);
        }
        // dereference and extract value
        if (i < point_y_length) {
            PyObject* y = PyTuple_GetItem(point_y, i);
            val_y = PyFloat_AsDouble(y);
        }
        diff = pow(val_y - val_x, 2.0);
        return_value += diff;
    }
    return_value = sqrt(return_value);
    return Py_BuildValue("d", return_value);
}


static PyObject* distances_octagonal_distance(PyObject* self, PyObject* args, PyObject* kwds) {
    // diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    // if len(diffs) != 2:
    //     raise TypeError('This distance is only valid in 2D')
    // diff_min = min(diffs)
    // diff_max = max(diffs)
    PyObject* point_x;
    PyObject* point_y;
    int point_x_length = -1;
    int point_y_length = -1;
    double val_x = 0.0;
    double val_y = 0.0;
    double diff = 0;
    long max_diff = LONG_MIN;
    long min_diff = LONG_MAX;
    double return_value = 0;
    long approximation = 0;
    long correction = 0;
    long corrected_approximation;

    static char *kws[] = { "x", "y", NULL };

    // Validate that the input correctly corresponds to the expected signature
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kws, &point_x, &point_y)) {
        return NULL;
    }

    // Find the maximum length
    point_x_length = Py_SIZE(point_x);
    point_y_length = Py_SIZE(point_y);
    if (point_x_length != 2) {
        char* error_message = extract_repr(point_x);
        strcat(error_message,  "is an invalid x parameter.  Only 2 dimensional distances are supported.");
        PyErr_SetString(&PyExc_ValueError, error_message);
        return NULL;
    }
    if (point_y_length != 2) {
        char* error_message = extract_repr(point_y);
        strcat(error_message,  "is an invalid y parameter.  Only 2 dimensional distances are supported.");
        PyErr_SetString(&PyExc_ValueError, error_message);
        return NULL;
    }

    // Iterate over each value and perform sum += (x(i) - y(i))^2
    // where
    //     if x(i) does not exist, then x(i) = 0
    //     and if y(i) does not exist, then y(i) = 0
    for (int i=0; i<2; i++) {
        val_x = 0;
        val_y = 0;
        diff = 0;
        // dereference and extract value
        if (i < point_x_length) {
            PyObject* x = PyTuple_GetItem(point_x, i);
            val_x = PyFloat_AsDouble(x);
        }
        // dereference and extract value
        if (i < point_y_length) {
            PyObject* y = PyTuple_GetItem(point_y, i);
            val_y = PyFloat_AsDouble(y);
        }
        if (val_x < val_y) {
            diff = val_y - val_x;
        } else {
            diff = val_x - val_y;
        }
        if (diff > max_diff) {
            max_diff = diff;
        }
        if (diff < min_diff) {
            min_diff = diff;
        }
    }
    approximation = max_diff * 1007 + min_diff * 441;
    if (max_diff < (min_diff << 4)) {
        correction = max_diff * 40;
    }
    corrected_approximation = approximation - correction;
    return_value = (corrected_approximation + 512) >> 10;
    return Py_BuildValue("d", return_value);
}


static PyMethodDef DistanceMethods[] = {
    {
        "manhattan_distance", (PyCFunction)distances_manhattan_distance, METH_VARARGS | METH_KEYWORDS,
         "Calculate a distance using the manhattan distance formula.\n"
         "\n"
         "Args:\n"
         "    x (int): point in space\n"
         "    y (int): point in space\n"
         "\n"
         "Returns:\n"
         "    int: distance between point x and point y"
    }, {
        "euclidean_distance", (PyCFunction)distances_euclidean_distance, METH_VARARGS | METH_KEYWORDS,
         "Calculate a distance using the euclidean distance formula.\n"
         "\n"
         "Args:\n"
         "    x (int): point in space\n"
         "    y (int): point in space\n"
         "\n"
         "Returns:\n"
         "    float: distance between point x and point y"
    }, {
        "octagonal_distance", (PyCFunction)distances_octagonal_distance, METH_VARARGS | METH_KEYWORDS,
         "Calculate a distance using the octagonal distance formula.\n"
         "\n"
         "Args:\n"
         "    x (int): point in space\n"
         "    y (int): point in space\n"
         "\n"
         "Returns:\n"
         "    int: distance between point x and point y"
    },
    {NULL, NULL, 0, NULL}  // Sentinel
};


static struct PyModuleDef distances =
{
    PyModuleDef_HEAD_INIT,
    "distances", /* name of module */
    "distance formulas",          /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    DistanceMethods
};


PyMODINIT_FUNC PyInit__distances(void)
{
    return PyModule_Create(&distances);
}