### RPM external cudnn-toolfile 7.6.1.34
Requires: cudnn

%prep

%build

%install

mkdir -p %{i}/etc/scram.d
cat << \EOF_TOOLFILE >%{i}/etc/scram.d/cudnn.xml
<tool name="cudnn" version="@TOOL_VERSION@">
  <info url="https://developer.nvidia.com/cudnn"/>
  <lib name="cudnn"/>
  <client>
    <environment name="CUDNN_BASE" default="@TOOL_ROOT@"/>
    <environment name="LIBDIR" default="$CUDNN_BASE/lib"/>
    <environment name="INCLUDE" default="$CUDNN_BASE/include"/>
  </client>
</tool>
EOF_TOOLFILE

## IMPORT scram-tools-post
