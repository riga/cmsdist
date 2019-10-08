### RPM external cudnn 7.6.1.34

Requires: cuda

AutoReq: no

%prep

%build

%install
rm -rf %_builddir/build
mkdir -p %_builddir/build

( cd %_builddir/build && tar -xzf /afs/cern.ch/work/m/mrieger/public/software/cudnn/cudnn-10.1-linux-x64-v7.6.3.30.tgz )

# create target directory structure
mkdir -p %{i}/lib
mkdir -p %{i}/include

# fix permissions
chmod -R ug+rwX %_builddir/build/cuda

# move files
mv -f %_builddir/build/cuda/lib64/libcudnn* %{i}/lib
mv -f %_builddir/build/cuda/include/cudnn.h %{i}/include

# copy files to the cuda directory as this is required by tensorflow (symlinks lead to failures)
cp -p -r %{i}/lib/* $CUDA_ROOT/lib64
cp -p -r %{i}/include/* $CUDA_ROOT/include
