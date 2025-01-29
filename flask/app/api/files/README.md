# Files Submodule

Pull Updates for All Submodules

If you want to pull updates for all submodules, use:

```
git submodule update --remote

```

This command fetches and updates your submodules to the latest commit on the branch specified in the .gitmodules file or the branch currently checked out within the submodule.

Pull Updates for a Specific Submodule

If you want to update a specific submodule only, specify the path to the submodule:

```
git submodule update --remote path/to/submodule

```
Replace path/to/submodule with the actual path to your submodule.

Commit the Submodule Update

After pulling the updates, you will need to commit the changes in your main project repository because the submodule's reference will have changed:

```
git commit -am "Updated submodule to latest commit"
```
