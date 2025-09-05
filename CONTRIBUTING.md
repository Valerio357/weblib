# Contributing to WebLib

First off, thank you for considering contributing to WebLib! It's people like you that make WebLib such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, [make one](https://github.com/Valerio357/weblib/issues/new)! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

### Fork & create a branch

If this is something you think you can fix, then [fork WebLib](https://github.com/Valerio357/weblib/fork) and create a branch with a descriptive name.

A good branch name would be (where issue #38 is the ticket you're working on):

```sh
git checkout -b 38-add-a-new-feature
```

### Get the test suite running

Make sure you're running the tests before you make any changes. See the Development Setup section in the `README.md` for instructions.

### Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first 😸

### Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with WebLib's master branch:

```sh
git remote add upstream git@github.com:Valerio357/weblib.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 38-add-a-new-feature
git rebase master
git push --force origin 38-add-a-new-feature
```

Finally, go to GitHub and [make a Pull Request](https://github.com/Valerio357/weblib/compare)

### Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing and merging, check out this guide on [syncing a fork](https://help.github.com/articles/syncing-a-fork).

## How to Contribute

We'd love to accept your patches and contributions to this project. There are just a few small guidelines you need to follow.

### Code of Conduct

This project and everyone participating in it is governed by the [WebLib Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [valeriodomenici93@gmail.com](mailto:valeriodomenici93@gmail.com).

### Code reviews

All submissions, including submissions by project members, require review. We use GitHub pull requests for this purpose. Consult [GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information on using pull requests.

### Community Guidelines

This project follows [Google's Open Source Community Guidelines](https://opensource.google/conduct/).
