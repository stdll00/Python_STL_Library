
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
        