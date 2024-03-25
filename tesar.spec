Name: tesar
Version: 2024.03.25
Release: 1%{?dist}

Summary: tesar
License: MIT
BuildArch: noarch

URL: https://github.com/danmyway/tesar
Source0: https://github.com/danmyway/tesar/releases/download/%{version}/tesar-%{version}.tar.gz

%generate_buildrequires
%pyproject_buildrequires

%description
tesar

%prep
%autosetup


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files tesar

%files -f %{pyproject_files}
%{_bindir}/tesar

%changelog
