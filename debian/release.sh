#!/bin/sh -e

PKG="powernap"
MAJOR=1

error() {
	echo "ERROR: $@"
	exit 1
}

head -n1 debian/changelog | grep "unreleased" || error "This version must be 'unreleased'"

./debian/rules get-orig-source
bzr bd
sed -i "s/) unreleased;/-0ubuntu1~ppa1) hardy;/" debian/changelog
bzr bd -S
sed -i "s/ppa1) hardy;/ppa2) intrepid;/" debian/changelog
bzr bd -S
sed -i "s/ppa2) intrepid;/ppa3) jaunty;/" debian/changelog
bzr bd -S
sed -i "s/~ppa3) jaunty;/) karmic;/" debian/changelog
bzr bd -S
minor=`head -n1 debian/changelog | sed "s/^.*($MAJOR.//" | sed "s/-.*$//"`
bzr tag --delete $MAJOR.$minor || true
bzr tag $MAJOR.$minor
newminor=`expr $minor + 1`
dch -v "$MAJOR.$newminor" "UNRELEASED"
sed -i "s/$MAJOR.$newminor) .*;/$MAJOR.$newminor) unreleased;/" debian/changelog

gpg --armor --sign --detach-sig ../"$PKG"_*.orig.tar.gz

echo
echo
echo "To test:"
echo "  sudo dpkg -i ../*.deb"
echo
echo "To upload PPA packages:"
echo "  dput $PKG-ppa ../*ppa*changes"
echo
echo "To commit and push:"
echo "  bzr cdiff"
echo "  bzr commit -m 'releasing $MAJOR.$minor, opening $MAJOR.$newminor' && bzr push lp:$PKG"
echo
echo "Publish tarball at:"
echo "  https://launchpad.net/$PKG/trunk/+addrelease"
echo
echo
