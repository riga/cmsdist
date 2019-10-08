### RPM external nccl-toolfile 2.4.8

Requires: nccl

%prep

%build

%install

mkdir -p %{i}/etc/scram.d

cat << \EOF_TOOLFILE >%{i}/etc/scram.d/nccl.xml
<tool name="nccl" version="@TOOL_VERSION@">
  <info url="https://developer.nvidia.com/nccl"/>
  <lib name="nccl"/>
  <client>
    <environment name="NCCL_BASE" default="@TOOL_ROOT@"/>
    <environment name="LIBDIR" default="$NCCL_BASE/lib"/>
    <environment name="INCLUDE" default="$NCCL_BASE/include"/>
  </client>
</tool>
EOF_TOOLFILE

## IMPORT scram-tools-post
