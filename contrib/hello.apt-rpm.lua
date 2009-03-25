#!/usr/bin/apt-get script
print ("Hello, Lua in Apt-RPM")

value = confget ("APT::Architecture")
print (value)

pkg = pkgfind("apt")
if pkg then
    print("Package "..pkgname(pkg).." exists!")
end 
