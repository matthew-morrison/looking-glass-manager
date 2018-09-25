# Maintainer: Matthew Morrison <mjmorris@protonmail.com>

pkgname=looking-glass-manager
pkgver=0.0.1
pkgrel=0
pkgdesc="Looking Glass Manager is a GUI frontend to the looking-glass-client KVM application."
url="https://github.com/matthew-morrison/looking-glass-manager"
arch=('x86_64')
license=('None')
depends=()
makedepends=()
source=("https://github.com/matthew-morrison/looking-glass-manager/archive/${pkgver}.tar.gz")
sha512sums=('a844feccab9f75f9983774deeda85837f91a40529c138d9ddb1d72300fcfaa9ae07a7c7ac79295bcf8557543caeb3a36fd622719b6ed7096219db0669fa4a2f4')


package() {
    cd "${srcdir}"
    mkdir -p "${pkgdir}/opt"
    cp -r looking-glass-manager "${pkgdir}/opt"
    mkdir -p "${pkgdir}/usr/local/bin"
    ln -s "/opt/looking-glass-manager-${pkgdir}/looking-glass-manager.py" "${pkgdir}/usr/local/bin/looking-glass-manager"
}