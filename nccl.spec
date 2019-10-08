### RPM external nccl 2.4.8

Requires: cuda

AutoReq: no

%prep

%build

%install
rm -rf %_builddir/build
mkdir -p %_builddir/build

( cd %_builddir/build && tar -Jxf /afs/cern.ch/work/m/mrieger/public/software/nccl/nccl_2.4.8-1+cuda10.1_x86_64.txz )

# create target directory structure
mkdir -p %{i}/lib
mkdir -p %{i}/include

# move files
mv -f %_builddir/build/nccl_%{realversion}*cuda*/lib/*.so* %{i}/lib
mv -f %_builddir/build/nccl_%{realversion}*cuda*/include/* %{i}/include

# copy files to the cuda directory as this is required by tensorflow (symlinks lead to failures)
cp -r -p %{i}/lib/*.so* $CUDA_ROOT/lib64
cp -r -p %{i}/include/* $CUDA_ROOT/include
