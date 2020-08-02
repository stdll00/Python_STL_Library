import os
import sys

python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

from typing import TypeVar, List, Generic, Tuple

T = TypeVar('T')  # Declare type variable


class MultiSet(Generic[T]):
    def __init__(self, arr: List[T] = None):
        if not arr:
            arr = []
        import multiset
        self.multiset = multiset
        self.object = self.multiset.construct_from_list(arr)

    def add(self, v: T):
        self.multiset.add(self.object, v)

    def get(self, v: T) -> int:
        return self.multiset.get(self.object, v)

    def size(self) -> int:
        return self.multiset.size(self.object, None)

    def remove(self, v: T):
        """
        C++ std::multiset:erase
        :param v:
        :return:
        """
        self.multiset.remove(self.object, v)

    def search_higher_equal(self, v):
        """
        C++ std::multiset::lower_bound
        :param v:
        :return:
        """
        return self.multiset.search_higher_equal(self.object, v)

    @staticmethod
    def build():
        code_multiset = r"""
        #include <Python.h>
        #include <vector>
        #include <set>
        #include <iostream>

        using namespace std;

        // 参考1: http://www.speedupcode.com/c-class-in-python3/
        // 参考2: https://qiita.com/junkoda/items/2b1eda7569186809ca14

        const static auto comp_pyobj = [](PyObject* const & lhs, PyObject* const & rhs){
            return Py_TYPE(lhs)->tp_richcompare(lhs, rhs, Py_LT) == Py_True;
        };

        struct MultiSet4PyObject{
            multiset<PyObject*, decltype(comp_pyobj)> st;
            MultiSet4PyObject() : st(comp_pyobj) {}
            MultiSet4PyObject(vector<PyObject*>& vec) : st(vec.begin(), vec.end(), comp_pyobj) {}
            ~MultiSet4PyObject(){
                for(PyObject* const & p : st){
                    Py_DECREF(p);
                }
            }
            void add(PyObject* x){
                Py_INCREF(x);
                st.insert(x);
            }
            void remove(PyObject* x){
                auto it = st.find(x);
                st.erase(it);
                Py_DECREF(*it);
            }

            int get(PyObject* x) const {
                if (st.find(x) == st.end()) {
                    return 0;
                }
                return st.count(x);
            }

            PyObject* search_higher_equal(PyObject* x) const {
                return *st.lower_bound(x);
            }
            
            int size() const {
                return st.size();
            }
        };

        void MultiSet4PyObject_free(PyObject *obj){
            MultiSet4PyObject* const p = (MultiSet4PyObject*) PyCapsule_GetPointer(obj, "MultiSet4PyObjectPtr");
            delete p;
        }
        PyObject* MultiSet4PyObject_construct(PyObject* self, PyObject* args){
            MultiSet4PyObject* ms = new MultiSet4PyObject();
            return PyCapsule_New((void*)ms, "MultiSet4PyObjectPtr", MultiSet4PyObject_free);
        }
        PyObject* MultiSet4PyObject_construct_from_list(PyObject* self, PyObject* args){
            PyObject* lst;
            if(!PyArg_ParseTuple(args, "O", &lst)) return NULL;
            int siz;
            if(PyList_Check(lst)) siz = PyList_GET_SIZE(lst);
            else if(PyTuple_Check(lst)) siz = PyTuple_GET_SIZE(lst);
            else return NULL;
            vector<PyObject*> vec(siz);
            for(int i=0; i<siz; i++){
                vec[i] = PyList_Check(lst) ? PyList_GET_ITEM(lst, i) : PyTuple_GET_ITEM(lst, i);
                Py_INCREF(vec[i]);
            }
            MultiSet4PyObject* ms = new MultiSet4PyObject(vec);
            return PyCapsule_New((void*)ms, "MultiSet4PyObjectPtr", MultiSet4PyObject_free);
        }
        PyObject* MultiSet4PyObject_add(PyObject* self, PyObject* args){
            PyObject *msCapsule, *x;
            if(!PyArg_ParseTuple(args, "OO", &msCapsule, &x)) return NULL;
            MultiSet4PyObject* ms = (MultiSet4PyObject*)PyCapsule_GetPointer(msCapsule, "MultiSet4PyObjectPtr");
            ms->add(x);
            return Py_BuildValue("");
        }
        PyObject* MultiSet4PyObject_remove(PyObject* self, PyObject* args){
            PyObject *msCapsule, *x;
            if(!PyArg_ParseTuple(args, "OO", &msCapsule, &x)) return NULL;
            MultiSet4PyObject* ms = (MultiSet4PyObject*)PyCapsule_GetPointer(msCapsule, "MultiSet4PyObjectPtr");
            ms->remove(x);
            return Py_BuildValue("");
        }
        PyObject* MultiSet4PyObject_get(PyObject* self, PyObject* args){
            PyObject *msCapsule, *x;
            if(!PyArg_ParseTuple(args, "OO", &msCapsule, &x)) return NULL;
            MultiSet4PyObject* ms = (MultiSet4PyObject*)PyCapsule_GetPointer(msCapsule, "MultiSet4PyObjectPtr");
            int v = ms->get(x);
            return Py_BuildValue("i", v);
        }

        PyObject* MultiSet4PyObject_search_higher_equal(PyObject* self, PyObject* args){
            PyObject *msCapsule, *x;
            if(!PyArg_ParseTuple(args, "OO", &msCapsule, &x)) return NULL;
            MultiSet4PyObject* ms = (MultiSet4PyObject*)PyCapsule_GetPointer(msCapsule, "MultiSet4PyObjectPtr");
            PyObject* res = ms->search_higher_equal(x);
            return Py_BuildValue("O", res);
        }
        
        PyObject* MultiSet4PyObject_size(PyObject* self, PyObject* args){
            PyObject *msCapsule, *x;
            if(!PyArg_ParseTuple(args, "OO", &msCapsule, &x)) return NULL;
            MultiSet4PyObject* ms = (MultiSet4PyObject*)PyCapsule_GetPointer(msCapsule, "MultiSet4PyObjectPtr");
            int res = ms->size();
            return Py_BuildValue("i", res);
        }

        static PyMethodDef MultiSetMethods[] = {
            {"construct", MultiSet4PyObject_construct, METH_VARARGS, "Create multiset object"},
            {"construct_from_list", MultiSet4PyObject_construct_from_list, METH_VARARGS, "Create multiset object from list"},
            {"add", MultiSet4PyObject_add, METH_VARARGS, "Add item"},
            {"get", MultiSet4PyObject_get, METH_VARARGS, "Get Item Count"},
            {"remove", MultiSet4PyObject_remove, METH_VARARGS, "Remove item"},
            {"search_higher_equal", MultiSet4PyObject_search_higher_equal, METH_VARARGS, "Search item"},
            {"size", MultiSet4PyObject_size, METH_VARARGS, "get size"},

            {NULL, NULL, 0, NULL} 
        };

        static struct PyModuleDef multisetmodule = {
            PyModuleDef_HEAD_INIT,
            "multiset", 
            NULL, 
            -1, 
            MultiSetMethods,
        };

        PyMODINIT_FUNC PyInit_multiset(void){
            return PyModule_Create(&multisetmodule);
        }
        """
        code_setup = r"""
from distutils.core import setup, Extension
module = Extension(
    "multiset",
    sources=["dist/multiset.cpp"],
    extra_compile_args=["-O3", "-march=native","-std=c++11"]
)
setup(
    name="MultiSetMethod",
    version="0.0.4",
    description="wrapper for C++ multiset",
    ext_modules=[module]
)
        """
        try:
            os.makedirs('dist')
        except FileExistsError:
            pass
        with open("dist/multiset.cpp", "w") as f:
            f.write(code_multiset)
        with open("dist/setup.py", "w") as f:
            f.write(code_setup)
        os.system(f"python{python_version} dist/setup.py build_ext --inplace ")

    @classmethod
    def simple_test(cls):
        ms: cls[Tuple[int, int]] = cls()
        assert ms.size() == 0
        ms.add((100, 100))
        ms.add((100, 100))
        assert ms.get((100, 100)) == 2
        assert ms.get((0, 100)) == 0
        assert ms.size() == 2


if __name__ == '__main__':
    if sys.argv[-1] == "ONLINE_JUDGE":
        MultiSet.build()
        exit()

