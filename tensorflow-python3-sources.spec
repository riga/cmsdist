### RPM external tensorflow-python3-sources 2.0.0

BuildRequires: bazel
Requires: gcc protobuf java-env python3 cuda cudnn nccl libjpeg-turbo eigen nasm py2-numpy py2-enum34 py2-mock py2-wheel py2-keras-applications py2-keras-preprocessing py2-setuptools py2-future

Source: https://github.com/tensorflow/tensorflow/archive/v%{realversion}.tar.gz

%prep

%setup -q -n tensorflow-%{realversion}

%build

export PYTHON_BIN_PATH="$(which python3)"
export USE_DEFAULT_PYTHON_LIB_PATH=1
export GCC_HOST_COMPILER_PATH="$(which gcc)"
export CC_OPT_FLAGS=-march=core2
export EIGEN_SOURCE=${EIGEN_SOURCE}
export PROTOBUF_SOURCE=${PROTOBUF_SOURCE}
export LIBJPEG_TURBO_SOURCE=${LIBJPEG_TURBO_SOURCE}
export EIGEN_STRIP_PREFIX=${EIGEN_STRIP_PREFIX}
export PROTOBUF_STRIP_PREFIX=${PROTOBUF_STRIP_PREFIX}
export LIBJPEG_TURBO_STRIP_PREFIX=${LIBJPEG_TURBO_STRIP_PREFIX}

export TF_NEED_JEMALLOC=0
export TF_NEED_HDFS=0
export TF_NEED_GCP=0
export TF_ENABLE_XLA=0
export TF_NEED_OPENCL=0
export TF_NEED_CUDA=1
export TF_NEED_VERBS=0
export TF_NEED_MKL=0
export TF_NEED_MPI=0
export TF_NEED_S3=0
export TF_NEED_GDR=0
export TF_NEED_OPENCL_SYCL=0
export TF_SET_ANDROID_WORKSPACE=false
export TF_NEED_KAFKA=false
export TF_NEED_AWS=0
export TF_DOWNLOAD_CLANG=0
export TF_NEED_IGNITE=0
export TF_NEED_ROCM=0
export TF_NEED_TENSORRT=0
export TF_CUDA_PATHS="$CUDA_ROOT"
export TF_CUDA_COMPUTE_CAPABILITIES="6.0,6.1,7.0,7.5"  # https://developer.nvidia.com/cuda-gpus#compute
export TF_CUDA_CLANG=0
export TF_NCCL_VERSION="$(echo $NCCL_VERSION | cut -d - -f 1)"

# the python targets do not use TF_CUDA_PATHS to find cuda but the library path
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CUDA_ROOT/lib64:$CUDA_ROOT/lib"

# clear the build dir and configure
rm -rf ../build
./configure

# define bazel options
BAZEL_OPTS="--output_user_root ../build build -s --verbose_failures --config=opt --config=v2 --config=cuda --cxxopt=-D_GLIBCXX_USE_CXX11_ABI=0 %{makeprocesses}"
BAZEL_EXTRA_OPTS="--action_env=PYTHONPATH=${PYTHON3PATH} --action_env=LD_LIBRARY_PATH --distinct_host_configuration=false"

# build tensorflow python targets
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/tools/pip_package:build_pip_package
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/python/tools:tools_pip
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/python/tools:import_pb_to_tensorboard

# build tensorflow targets
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow:libtensorflow_cc.so
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/tools/lib_package:libtensorflow
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/tools/graph_transforms:transform_graph
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/compiler/tf2xla:tf2xla
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/compiler/xla:cpu_function_runtime
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/compiler/tf2xla:xla_compiled_cpu_function
%ifnarch ppc64le
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow/compiler/aot:tfcompile
%endif
bazel $BAZEL_OPTS $BAZEL_EXTRA_OPTS //tensorflow:install_headers

# download dependencies used by tensorflow, some headers are copied to the include dir later on
# (not required at the moment)
# tensorflow/contrib/makefile/download_dependencies.sh

bazel shutdown

# rebuild *.pb.{h|cc} files using the external protobuf compiler
chmod -R a+rwX $PWD/bazel-bin/tensorflow/include
for f in $(find tensorflow -name "*.proto")
do
    protoc --cpp_out=$PWD/bazel-bin/tensorflow/include $f
done

%install

# define and create empty target directories
outdir="$PWD/out"
bindir="$outdir/bin"
incdir="$outdir/include"
libdir="$outdir/lib"
rm -rf $bindir $incdir $libdir
mkdir -p $bindir $incdir $libdir

# copy targets
srcdir="$PWD/bazel-bin/tensorflow"

cp -p $srcdir/libtensorflow_cc.so.%{realversion} $libdir/libtensorflow_cc.so
cp -p $srcdir/libtensorflow_framework.so.%{realversion} $libdir/libtensorflow_framework.so
cp -p $srcdir/libtensorflow.so.%{realversion} $libdir/libtensorflow.so
cp -p $srcdir/compiler/tf2xla/libtf2xla.so $libdir
cp -p $srcdir/compiler/tf2xla/libxla_compiled_cpu_function.so $libdir
cp -p $srcdir/compiler/xla/libcpu_function_runtime.so $libdir

# libtensorflow.so and libtensorflow_cc.so are linked to libtensorflow_framework.so.MAJOR
tf_version_major="$(echo "%{realversion}" | cut -d . -f 1)"
ln -s "$libdir/libtensorflow_framework.so" "$libdir/libtensorflow_framework.so.$tf_version_major"

%ifnarch ppc64le
cp -p $srcdir/compiler/aot/tfcompile $bindir
%endif

for name in tensorflow absl re2 third_party
do
    cp -r -p $srcdir/include/$name $incdir
done

# copy headers from downloaded dependencies
copy_headers() {
    local origin="$PWD"
    cd "$1"
    for header_file in $(find $2 -name *.h)
    do
        local header_dir="$incdir/$(dirname "$header_file")"
        mkdir -p "$header_dir"
        cp -p "$header_file" "$header_dir"
    done
    cd "$origin"
}
copy_headers "$PWD" tensorflow/compiler
# do not copy the protobuf headers as we use the version in cmsdist
# copy_headers "$PWD/tensorflow/contrib/makefile/downloads/protobuf/src" google

# create the wheel file that is installed in py2-tensorflow
bazel-bin/tensorflow/tools/pip_package/build_pip_package %{i}

# bundle and save output files as expected by tensorflow.spec
cd $outdir
tar cfz %{i}/libtensorflow_cc.tar.gz .
