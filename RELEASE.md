To release a new version of Spyder Reports:

* Create an issue announcing the incoming release

* Close the respective milestone in GitHub

* git checkout master

* git fetch upstream && git merge upstream/master

* Update CHANGELOG.md with loghub

* Update `_version.py` (set release version, remove 'dev0')

* git add . && git commit -m 'Release X.X.X'

* python setup.py sdist upload

* python setup.py bdist_wheel upload

* git tag -a vX.X.X -m 'Release X.X.X'

* Update `_version.py` (add 'dev0' and increment minor)

* git add . && git commit -m 'Back to work'

* git push upstream master && git push upstream --tags

* Publish release announcement in the Spyder Google Group

* Publish a message in our social media (Twitter, Facebook, and Google Plus)

* **Note**: Before using these commands be sure that the distribution is
complete i.e all the needed files are in the distribution for uploading.
Also, do not take the dist files into account when doing the commits.
