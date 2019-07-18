### RPM external cudnn %{fullversion}

%define fullversion 7.6.1.34
%define cudnnversion %(echo %realversion | cut -d. -f 1)

Requires: cuda

# wrong filename after download
#Source0: https://cernbox.cern.ch/index.php/s/pHHOxPpG55N41jl/download?path=%2Fcudnn&files=cudnn-10.1-linux-x64-v7.6.1.34.tgz

AutoReq: no

%prep

%build

%install
rm -rf %_builddir/build
mkdir -p %_builddir/build

( cd %_builddir/build && tar -xzf /afs/cern.ch/work/m/mrieger/public/software/cudnn/cudnn-10.1-linux-x64-v7.6.1.34.tgz )

# create target directory structure
mkdir -p %{i}/lib64
mkdir -p %{i}/include

# move stuff
#mv %_builddir/build/cuda/lib64/libcudnn* %{i}/lib64/
#mv %_builddir/build/cuda/include/cudnn.h %{i}/include/
mv %_builddir/build/cuda/lib64/libcudnn* $CUDA_ROOT/lib64/
mv %_builddir/build/cuda/include/cudnn.h $CUDA_ROOT/include/

# permissions
#chmod -R a+rX %{i}/lib64
#chmod -R a+r %{i}/include
# TODO: fix permissions?
chmod -R a+rX $CUDA_ROOT/lib64
chmod -R a+rX $CUDA_ROOT/include
